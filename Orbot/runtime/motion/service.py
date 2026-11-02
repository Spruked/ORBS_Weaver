import hmac
import os
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from .presentation import PresentationMotion
from .morb_guidance import MorbGuidance
from .attention import DesktopAttention
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from runtime.shared.diagnostics import RuntimeDiagnostics, metric

diagnostics = RuntimeDiagnostics("motion")
presentation = PresentationMotion()
morbs = MorbGuidance()
attention = DesktopAttention()
last_presentation_step = None

app = FastAPI(title="Orbot Motion", docs_url=None, redoc_url=None)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"])


@app.get("/health")
def health():
    return {"runtime": "motion", "ready": True, "mode": "presentation_only",
            "presentation_motion_available": True, "command_execution_enabled": False, "execution_authority": False, "hardware_connected": False}


@app.post("/commands")
def command():
    raise HTTPException(503, "Motion disabled until canonical Vault permits and live safety checks are wired")


class Monitor(BaseModel):
    model_config = {"extra": "forbid"}
    x: int = Field(ge=-100000, le=100000)
    y: int = Field(ge=-100000, le=100000)
    width: int = Field(ge=1, le=50000)
    height: int = Field(ge=1, le=50000)
    scale: float = Field(gt=0, le=10, allow_inf_nan=False)

class Cursor(BaseModel):
    model_config = {"extra": "forbid"}
    x: int = Field(ge=-100000, le=100000)
    y: int = Field(ge=-100000, le=100000)

class Frame(BaseModel):
    model_config = {"extra": "forbid"}
    x: int = Field(ge=-100000, le=100000)
    y: int = Field(ge=-100000, le=100000)
    width: int = Field(ge=1, le=5000)
    height: int = Field(ge=1, le=5000)
    orb_x: float = Field(ge=0, le=5000, allow_inf_nan=False)
    orb_y: float = Field(ge=0, le=5000, allow_inf_nan=False)
    orb_radius: float = Field(gt=0, le=2500, allow_inf_nan=False)
    cursor: Cursor
    interaction: bool
    monitors: list[Monitor] = Field(min_length=1, max_length=16)
    foreground_app: str | None = Field(default=None, max_length=260)
    window_title: str | None = Field(default=None, max_length=512)
    foreground_rect: dict | None = None
    idle_ms: int | None = Field(default=None, ge=0, le=604800000)
    voice_state: str | None = Field(default=None, max_length=40)

def desktop_auth(authorization):
    root = Path(__file__).resolve().parents[2]
    token_path = Path(os.getenv('ORBOT_VAULT_TOKEN_FILE', str(root.parent / 'orbs_vault_system/.local/host-memory.token')))
    try:
        token = token_path.read_text(encoding='utf-8').strip()
    except OSError:
        raise HTTPException(503, 'Existing desktop credential unavailable')
    if not token or not hmac.compare_digest(authorization or '', 'Bearer '+token):
        raise HTTPException(401, 'Existing desktop credential required')

class GuidanceTarget(BaseModel):
    model_config = {"extra": "forbid"}
    x: int = Field(ge=-100000, le=100000)
    y: int = Field(ge=-100000, le=100000)

class PresentationAuthority(BaseModel):
    model_config = {"extra": "forbid"}
    authority: str = Field(pattern="^(ambient|hold|guided)$")
    target: GuidanceTarget | None = None

@app.post('/presentation/authority')
def set_presentation_authority(req: PresentationAuthority, authorization: str | None = Header(default=None)):
    desktop_auth(authorization)
    if req.authority=='guided' and req.target is None:
        raise HTTPException(422, 'Guided positioning requires a target coordinate')
    attention.manual_override()
    try:
        target=(req.target.x,req.target.y) if req.target else None
        presentation.set_authority(req.authority,target)
        return {'authority':req.authority,'target':target,'execution_authority':False}
    except ValueError as error:
        raise HTTPException(422,str(error))

@app.post('/presentation/morbs/assign')
def assign_guidance(target: GuidanceTarget, authorization: str | None = Header(default=None)):
    desktop_auth(authorization)
    if last_presentation_step is None or time.monotonic()-last_presentation_step > 2:
        raise HTTPException(409, 'Orbot presentation is not active')
    try:
        return {'id':morbs.assign(target.x, target.y), 'meaning':'unverified_coordinate', 'execution_authority':False}
    except ValueError as e:
        raise HTTPException(409, str(e))

@app.post('/presentation/morbs/clear')
def clear_guidance(authorization: str | None = Header(default=None)):
    global last_presentation_step
    desktop_auth(authorization); morbs.clear(); last_presentation_step = None
    return {'cleared':True, 'execution_authority':False}

@app.post('/presentation/step')
def presentation_step(frame: Frame, authorization: str | None = Header(default=None)):
    global last_presentation_step
    desktop_auth(authorization)
    data=frame.model_dump()
    result = presentation.step(data)
    result['morbs'] = morbs.step(data)
    result['attention'] = attention.update(data, presentation)
    last_presentation_step = time.monotonic()
    return result

class AttentionFeedback(BaseModel):
    model_config = {"extra": "forbid"}
    declined: bool

@app.post('/presentation/attention/feedback')
def attention_feedback(req: AttentionFeedback, authorization: str | None = Header(default=None)):
    desktop_auth(authorization)
    result = attention.feedback(req.declined)
    if result.get('accepted') and presentation.authority == 'hold':
        presentation.set_authority('ambient')
    return result


@app.get("/diagnostics")
def runtime_diagnostics():
    result = diagnostics.snapshot()
    result["metrics"]["enabled"] = metric(False, "motion")
    result["metrics"]["disabled_reason"] = metric(
        "Canonical Vault permits and live safety checks are not wired", "motion")
    result["metrics"]["presentation_active"] = metric(
        last_presentation_step is not None and time.monotonic()-last_presentation_step < 2, "motion.presentation")
    active = result["metrics"]["presentation_active"]["value"]
    result["metrics"]["presentation_state"] = metric(presentation.last_result.get('state') if active else 'inactive', "motion.presentation")
    result["metrics"]["presentation_authority"] = metric(presentation.authority if active else None, "motion.presentation")
    for key in ('velocity', 'nudge_speed', 'monitor_index', 'destination_monitor', 'destination', 'arrivals'):
        result["metrics"]["presentation_"+key] = metric(presentation.last_result.get(key) if active else None, "motion.presentation")
    result["metrics"]["presentation_writer"] = metric('orbot_native_host', "motion.presentation")
    result["metrics"]["attention_phase"] = metric(attention.result.get('phase'), "motion.attention")
    result["metrics"]["attention_work_monitor"] = metric(attention.result.get('work_monitor'), "motion.attention")
    result["metrics"]["attention_perches"] = metric(attention.result.get('perches'), "motion.attention")
    result["metrics"]["presentation_work_targets"] = metric(len(presentation.work_targets), "motion.presentation")
    return result
