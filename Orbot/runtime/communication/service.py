"""Loopback-only, bounded conversation service. No tool or motion authority."""
from __future__ import annotations

import asyncio
import base64
import logging
import os
import hmac
import time
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .providers import LlamaCppProvider, QwenSpeechProvider, RemoteChatProvider
from .voice_diagnostics import voice_diagnostics
from .voice_turns import voice_turns, VoiceCancelled
from .qwen_gpu import QwenGpuCapacityError
from .memory import get_memory, dock_token
from runtime.shared.health import peer_status
from .cochlear import CochlearInput
from .integrations import retrieve_owner_requested_evidence
from .epistemic_field import observe_field
from runtime.shared.diagnostics import RuntimeDiagnostics
from runtime.shared.diagnostics import metric
from runtime.cognition_governance.inculcation import FoundationError, loader

diagnostics = RuntimeDiagnostics("communication")

app = FastAPI(title="Orbot Communication", docs_url=None, redoc_url=None)
origins = ["http://127.0.0.1:1420", "http://localhost:1420", "http://tauri.localhost", "tauri://localhost"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"])
provider_mode = os.getenv("ORBOT_INTELLIGENCE_PROVIDER", "local")
if provider_mode not in {"local", "remote"}:
    raise ValueError("ORBOT_INTELLIGENCE_PROVIDER must be local or remote")
language = (RemoteChatProvider() if provider_mode == "remote" else
            LlamaCppProvider(os.getenv("ORBOT_LLAMA_URL", "http://127.0.0.1:16520/v1")))
speech_provider = os.getenv("ORBOT_TTS_PROVIDER", "qwen")
if speech_provider != "qwen":
    raise ValueError("ORBOT_TTS_PROVIDER must be qwen; speech fallback is disabled")
speech = QwenSpeechProvider()
busy = asyncio.Lock()
hearing = CochlearInput()
hearing_busy = asyncio.Lock()
attention_busy = asyncio.Lock()
foundation_preflight = {"fits": None, "reason": "Inference capacity not measured"}


@app.on_event("startup")
def initialize_memory():
    global foundation_preflight
    loader.load()
    get_memory()
    dock_token()
    try:
        foundation_preflight = language.initialize_foundation()
    except Exception as error:
        foundation_preflight = {"fits": False, "reason": str(error)}


@app.exception_handler(FoundationError)
async def invalid_foundation(_request, error):
    return JSONResponse({"detail": "Professional foundation unavailable: " + str(error)}, status_code=503)


@app.on_event("shutdown")
def finalize_memory():
    get_memory().close_all()


@app.middleware("http")
async def local_boundary(request: Request, call_next):
    origin = request.headers.get("origin")
    if origin and origin not in origins:
        return JSONResponse({"detail": "Origin not allowed"}, status_code=403)
    if request.method == "POST":
        if request.headers.get("content-type", "").split(";")[0] != "application/json":
            return JSONResponse({"detail": "JSON required"}, status_code=415)
        body = await request.body()
        limit = 8 * 1024 * 1024 if request.url.path.startswith(("/memory/", "/voice/")) else 16384
        if len(body) > limit:
            return JSONResponse({"detail": "Request too large"}, status_code=413)
    return await call_next(request)


class ConversationRequest(BaseModel):
    model_config = {"extra": "forbid"}
    text: str = Field(min_length=1, max_length=2000)
    speak: bool = False
    session_id: str | None = Field(default=None, max_length=100)
    important: bool = False
    priority: Literal["high", "medium", "low"] = "low"
    objective: str | None = Field(default=None, min_length=1, max_length=1000)


class VoiceInput(BaseModel):
    model_config = {"extra": "forbid"}
    session_id: str = Field(min_length=1, max_length=100)
    audio_wav: str = Field(max_length=8000000)
    turn_id: str | None = Field(default=None, min_length=1, max_length=80, pattern=r"^[a-zA-Z0-9-]+$")


class AttentionOffer(BaseModel):
    model_config = {"extra": "forbid"}
    session_id: str = Field(min_length=1, max_length=100)
    application: str = Field(min_length=1, max_length=260)
    window_title: str = Field(default="", max_length=240)
    stable_seconds: int = Field(ge=0, le=86400)


@app.post('/voice/input')
async def voice_input(req: VoiceInput):
    if hearing_busy.locked():
        raise HTTPException(429, 'Communication is busy; wait for the current turn to finish')
    if attention_busy.locked():
        async with attention_busy:
            pass
    if hearing_busy.locked() or busy.locked():
        raise HTTPException(429, 'Communication is busy; wait for the current turn to finish')
    memory = get_memory()
    try:
        history = memory.items(req.session_id)
        turn = voice_turns.begin(req.session_id, req.turn_id)
    except ValueError as error:
        raise HTTPException(409, str(error))
    try:
        async with hearing_busy:
            started = time.monotonic()
            voice_diagnostics.set("server_stage", "recognizing")
            voice_diagnostics.set("turn_id", turn.turn_id)
            voice_diagnostics.set("last_error", "")
            try:
                profile = next((item['hearing']['hearing_profile'] for item in reversed(history)
                                if 'hearing' in item), None)
                audio = base64.b64decode(req.audio_wav, validate=True)
                trace = await asyncio.to_thread(hearing.transcribe, audio, profile)
                turn.check()
            except VoiceCancelled:
                raise
            except ValueError as error:
                voice_diagnostics.set("server_stage", "recognition_rejected")
                voice_diagnostics.set("last_error", str(error))
                voice_diagnostics.increment("recognition_failures")
                raise HTTPException(422, str(error))
            except Exception:
                voice_diagnostics.set("server_stage", "recognition_failed")
                voice_diagnostics.set("last_error", "Local hearing failed. Check microphone level and retry.")
                voice_diagnostics.increment("recognition_failures")
                logging.exception('Local hearing failed')
                raise HTTPException(503, 'Local hearing unavailable')
            voice_diagnostics.set("recognition_ms", round((time.monotonic()-started)*1000))
            voice_diagnostics.increment("recognized_inputs")
            voice_diagnostics.set("stt_loaded", hearing.model is not None)
            voice_diagnostics.set("server_stage", "forming_response")
            memory.remember(req.session_id, {'hearing': trace, 'voice_turn_id':turn.turn_id}, priority='low')
            # Inferred corrections remain observations; never impersonate what the owner said.
            spoken_text = trace.get('original_transcript') or trace['text']
            result = await _conversation(ConversationRequest(text=spoken_text, session_id=req.session_id, speak=True), turn)
            turn.check()
            result['turn_id'] = turn.turn_id
            result['hearing'] = {key: trace.get(key) for key in ('text', 'original_transcript', 'processor', 'verified')}
            voice_diagnostics.increment("completed_round_trips")
            return result
    except VoiceCancelled:
        voice_diagnostics.set("server_stage", "cancelled")
        voice_diagnostics.increment("cancelled_turns")
        raise HTTPException(409, 'Voice turn cancelled; session preserved')
    finally:
        voice_turns.end(turn)


@app.post('/attention/offer')
async def attention_offer(req: AttentionOffer, request: Request):
    """Return one local spoken invitation without fabricating or retaining a user turn."""
    require_dock(request)
    if busy.locked() or hearing_busy.locked() or attention_busy.locked():
        raise HTTPException(409, "Communication is busy; attention offer withheld")
    async with attention_busy:
        if busy.locked() or hearing_busy.locked():
            raise HTTPException(409, "Communication is busy; attention offer withheld")
        async with busy:
            memory = get_memory()
            foundation = loader.load()
            try:
                history = memory.items(req.session_id)
                recall = memory.recall(req.session_id, req.application, limit=3)
            except ValueError as error:
                raise HTTPException(409, str(error))
            observation = {"application": req.application, "window_title": req.window_title,
                           "stable_seconds": req.stable_seconds, "source": "volatile_local_foreground_observation",
                           "saved_to_memory": False, "document_contents_observed": False}
            prompt = ("This is a runtime initiated, brief spoken invitation, not a statement from the owner. "
                      "Based only on the supplied volatile foreground application observation, offer to help. "
                      "Use a specific description only if the application/window label supports it; otherwise ask a general question. "
                      "Do not claim to know document contents, the owner's task, or intent. Keep it to one short sentence. "
                      "Observation: " + json.dumps(observation, ensure_ascii=False))
            try:
                reply = await asyncio.to_thread(language.reply, prompt, history, recall["results"],
                    turn_context={"foundation_sha256": foundation.sha256,
                                  "channel": "voice", "kind": "ephemeral_attention_offer",
                                  "desktop_observation": observation,
                                  "execution_authority": False})
                if loader.load().sha256 != foundation.sha256:
                    raise FoundationError("Foundation changed during attention offer; response withheld")
                reply = reply[:300]
                wav = await asyncio.to_thread(speech.synthesize, reply)
            except Exception as error:
                logging.warning("Attention offer withheld: %s", type(error).__name__)
                raise HTTPException(503, "Local attention response unavailable; no offer was spoken")
            return {"text": reply, "audio_wav": base64.b64encode(wav).decode("ascii"),
                    "ephemeral": True, "observation_saved": False, "execution_authority": False}


@app.post("/sessions")
def start_session():
    return {"session_id": get_memory().start("orbot-conversation")}


class SessionEnd(BaseModel):
    session_id: str = Field(max_length=100)


@app.post("/sessions/end")
def end_session(req: SessionEnd):
    try:
        review = get_memory().end(req.session_id)
    except ValueError as error:
        raise HTTPException(404, str(error))
    return {"closed": True, "short_term_cleared": True, "close_review": review}


@app.get("/sessions/{session_id}/caches")
def session_caches(session_id: str):
    try:
        return get_memory().cache_status(session_id)
    except ValueError as error:
        raise HTTPException(409, str(error))


def require_dock(request: Request):
    expected = "Bearer " + dock_token()
    if not hmac.compare_digest(request.headers.get("Authorization", ""), expected):
        raise HTTPException(401, "Dock Vault credentials required")


class AudioInputDevice(BaseModel):
    model_config = {"extra":"forbid"}
    device_id: str = Field(max_length=256)
    label: str = Field(max_length=200)


class VoiceClientEvent(BaseModel):
    model_config = {"extra": "forbid"}
    state: Literal["idle", "opening microphone", "listening", "thinking", "speaking", "blocked"]
    microphone: bool | None = None
    sample_rate: int | None = Field(default=None, ge=8000, le=192000)
    capture_ms: int | None = Field(default=None, ge=0, le=30000)
    playback: Literal["started", "ended", "failed", "interrupted"] | None = None
    error_name: str | None = Field(default=None, max_length=80)
    error_message: str | None = Field(default=None, max_length=500)
    input_label: str | None = Field(default=None, max_length=200)
    capture_id: str | None = Field(default=None, max_length=80)
    input_devices: list[AudioInputDevice] | None = Field(default=None, max_length=32)
    input_rms: float | None = Field(default=None, ge=0, le=1)
    playback_seconds: float | None = Field(default=None, ge=0, le=3600)


class SynthesisTest(BaseModel):
    model_config = {"extra": "forbid"}
    text: str = Field(min_length=1, max_length=300)


class PresentationSettings(BaseModel):
    model_config = {"extra": "forbid"}
    schema_version: Literal[1] = 1
    profile_id: str = Field(default="", max_length=100)
    standard_diameter: int = Field(default=240, ge=80, le=350)
    minimum_diameter: int = Field(default=80, ge=80, le=350)
    maximum_diameter: int = Field(default=350, ge=80, le=350)
    auto_resize: bool = True
    resize_smoothness: float = Field(default=.6, ge=0, le=1, allow_inf_nan=False)
    shape: Literal["sphere", "liquid", "hexagon"] = "sphere"
    shape_variation: bool = False
    shape_frequency: Literal["rare", "occasional", "frequent"] = "occasional"


class PresentationSettingsWrite(BaseModel):
    model_config = {"extra": "forbid"}
    value: PresentationSettings
    expected_entry_id: str | None = None


@app.get("/presentation/preferences")
def presentation_preferences(request: Request):
    require_dock(request)
    memory = get_memory()
    with memory.lock:
        value = memory.collection("dock.presentation_preferences")
        settings = PresentationSettings.model_validate(value or {})
        settings.shape_variation = False
        return {"value": settings.model_dump(),
                "entry_id": memory.collection_revision("dock.presentation_preferences")}


@app.post("/presentation/preferences")
def save_presentation_preferences(req: PresentationSettingsWrite, request: Request):
    require_dock(request)
    settings = req.value
    settings.shape_variation = False
    if not settings.minimum_diameter <= settings.standard_diameter <= settings.maximum_diameter:
        raise HTTPException(422, "Sizes must satisfy minimum <= standard <= maximum")
    try:
        result = get_memory().save_collection("dock.presentation_preferences", settings.model_dump(),
            "dock-station", "Owner updated presentation preferences", req.expected_entry_id)
        return {"value": settings.model_dump(), "entry_id": result["entry_id"]}
    except ValueError as error:
        raise HTTPException(409, str(error))


@app.get("/voice/preferences")
def voice_preferences(request: Request):
    require_dock(request)
    memory = get_memory()
    with memory.lock:
        return {"value":memory.collection("dock.voice_preferences") or {"device_id":"","label":os.getenv("ORBOT_AUDIO_INPUT_LABEL","System default")},
                "entry_id":memory.collection_revision("dock.voice_preferences")}


@app.post("/voice/preferences")
def save_voice_preferences(value: AudioInputDevice, request: Request):
    require_dock(request)
    memory = get_memory()
    with memory.lock:
        return memory.save_collection("dock.voice_preferences",value.model_dump(),"dock-station",
                                      "Owner selected microphone",memory.collection_revision("dock.voice_preferences"))


@app.get("/voice/last-turn")
def last_voice_turn(request: Request):
    """Owner-only inspection of the current session, not a second transcript log."""
    require_dock(request)
    memory = get_memory()
    with memory.lock:
        session = memory.embodiment_session
        if session is None:
            return {"available": False}
        history = memory.items(session)
        heard = next((item for item in reversed(history) if item.get("voice_turn_id") and "hearing" in item), None)
        if heard is None:
            return {"available":False}
        turn_id = heard["voice_turn_id"]
        reply = next((item for item in reversed(history) if item.get("voice_turn_id")==turn_id and "assistant" in item), {})
        return {"available":True,"turn_id":turn_id,
                "hearing":{key:heard["hearing"].get(key) for key in ("text","original_transcript","verified","processor")},
                "response_text":reply.get("assistant"),"foundation_sha256":reply.get("inculcation_sha256"),
                "verification":"session_observations_not_verified_relationship_facts","execution_authority":False}


class VoiceCancel(BaseModel):
    model_config = {"extra": "forbid"}
    session_id: str | None = Field(default=None, max_length=100)
    turn_id: str | None = Field(default=None, max_length=80)


@app.post("/voice/cancel")
def cancel_voice(req: VoiceCancel, request: Request):
    require_dock(request)
    session_id = req.session_id or get_memory().embodiment_session
    cancelled = voice_turns.cancel(session_id, req.turn_id)
    if cancelled:
        voice_diagnostics.set("server_stage", "cancelling")
    return {"cancel_requested": cancelled, "session_preserved": True, "execution_authority": False}


@app.post("/voice/synthesize")
async def synthesize_test(req: SynthesisTest, request: Request):
    require_dock(request)
    if busy.locked():
        raise HTTPException(429, "Communication is busy")
    async with busy:
        voice_diagnostics.set("server_stage", "synthesizing_test")
        started = time.monotonic()
        try:
            audio = await asyncio.to_thread(speech.synthesize, req.text)
        except Exception as error:
            reason = str(error) if isinstance(error,QwenGpuCapacityError) else "Qwen3-TTS synthesis failed. Check local model and GPU diagnostics."
            voice_diagnostics.set("server_stage", "synthesis_failed")
            voice_diagnostics.set("last_error", reason)
            raise HTTPException(503, reason)
        voice_diagnostics.set("server_stage", "test_audio_generated")
        voice_diagnostics.set("tts_generation_ms", round((time.monotonic()-started)*1000))
        return {"audio_wav": base64.b64encode(audio).decode("ascii"), "provider": speech_provider,
                "latency_ms": round((time.monotonic()-started)*1000), "playback_verified": False}


@app.post("/voice/events")
def voice_client_event(event: VoiceClientEvent, request: Request):
    require_dock(request)
    for key, value in event.model_dump(exclude_none=True).items():
        voice_diagnostics.set("client." + key, value, "orb_webview_report")
    return {"recorded": True, "verification": "client_report_not_hardware_audit", "execution_authority": False}


@app.post("/sessions/embodiment")
def active_embodiment_session(request: Request):
    require_dock(request)
    return {"session_id": get_memory().start_embodiment()}


@app.get("/sessions/embodiment")
def current_embodiment_session(request: Request):
    require_dock(request)
    return {"session_id": get_memory().embodiment_session}


class RuntimeShutdown(BaseModel):
    process_instance_id: str


@app.post("/lifecycle/shutdown")
def shutdown_owned_runtime(req: RuntimeShutdown, request: Request):
    require_dock(request)
    if req.process_instance_id != diagnostics.instance:
        raise HTTPException(409, "Runtime instance changed; shutdown refused")
    server = getattr(app.state, "server", None)
    if server is None:
        raise HTTPException(503, "Runtime is not managed by its native server entrypoint")
    reviews = get_memory().close_all()
    server.should_exit = True
    return {"stopping": True, "close_reviews": reviews}


@app.get("/memory/collections/{name}")
def read_collection(name: str, request: Request):
    require_dock(request)
    if name not in {"profiles", "versions", "conversations", "statistics", "diagnostics", "skins", "desktop_events"}:
        raise HTTPException(404, "Unknown collection")
    memory = get_memory()
    with memory.lock:
        return {"value": memory.collection("dock." + name), "entry_id": memory.collection_revision("dock." + name)}


class CollectionWrite(BaseModel):
    payload: dict | list
    reason: str = Field(min_length=1, max_length=300)
    expected_entry_id: str | None = None


@app.post("/memory/collections/{name}")
def write_collection(name: str, req: CollectionWrite, request: Request):
    require_dock(request)
    if name not in {"profiles", "versions", "conversations", "statistics", "diagnostics", "skins", "desktop_events"}:
        raise HTTPException(404, "Unknown collection")
    try:
        return get_memory().save_collection("dock." + name, req.payload, "dock-station", req.reason, req.expected_entry_id)
    except ValueError as error:
        raise HTTPException(409, str(error))


class ObservationWrite(BaseModel):
    session_id: str
    payload: dict
    important: bool = False
    reason: str = ""
    priority: Literal["high", "medium", "low"] = "low"


class RecallRequest(BaseModel):
    model_config = {"extra": "forbid"}
    session_id: str = Field(min_length=1, max_length=100)
    query: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=5, ge=1, le=10)


@app.post("/memory/recall")
def recall_memory(req: RecallRequest):
    try:
        return get_memory().recall(req.session_id, req.query, req.limit)
    except ValueError as error:
        raise HTTPException(409, str(error))


@app.get("/memory/knowledge/status")
def knowledge_status():
    return get_memory().knowledge_status()


@app.post("/memory/observations")
def record_observation(req: ObservationWrite, request: Request):
    require_dock(request)
    try:
        return get_memory().remember(req.session_id, req.payload, req.important, req.reason, req.priority)
    except ValueError as error:
        raise HTTPException(409, str(error))


@app.get("/status")
async def status():
    governance = await asyncio.to_thread(peer_status, "cognition_governance")
    motion = await asyncio.to_thread(peer_status, "motion")
    try:
        models = await asyncio.to_thread(language.models)
        connected = bool(models)
    except Exception:
        models, connected = [], False
    return {
        "llm_connected": connected, "models": models,
        "tts_model": speech.model_id, "tts_loaded": speech.loaded,
        "tts_device": speech.active_device,
        "tts_precision": speech.active_precision,
        "external_api_enabled": provider_mode == "remote", "provider": provider_mode,
        "governance_connected": governance.get("ready", False),
        "runtimes": {"cognition_governance": governance, "motion": motion},
        "memory_skg_connected": True,
        "execution_authority": False,
        "professional_foundation": loader.load().status(),
        "professional_context": getattr(language, "context_status", foundation_preflight),
    }


@app.get("/inculcation/status")
def inculcation_status(request: Request):
    require_dock(request)
    memory = get_memory()
    memory.bind_professional_foundation(loader.load())
    return {**memory.professional_foundation_status(),
            "context": getattr(language, "context_status", foundation_preflight),
            "application_snapshot_loads": loader.loads,
            "governance_integration": {"tpc": "not_integrated", "sealed_doctrine": "not_verified",
                                       "permit_authority": False}}


@app.get("/health")
def health():
    foundation = loader.load()
    context = foundation_preflight
    return {"runtime": "communication", "ready": context.get("fits") is True and
            context.get("foundation_sha256") == foundation.sha256,
            "execution_authority": False, "professional_foundation": foundation.status(),
            "process_instance_id": diagnostics.instance,
            "professional_context": context}


@app.get("/diagnostics")
def runtime_diagnostics():
    result = diagnostics.snapshot()
    result["metrics"].update(voice_diagnostics.snapshot())
    for key, value in {"tts_provider": speech_provider, "tts_model": speech.model_id,
                       "tts_loaded": speech.loaded, "tts_device": speech.active_device,
        "tts_precision": speech.active_precision,
                       "tts_precision": speech.active_precision, "tts_cpu_threads": speech.active_threads,
                       "tts_execution_mode": speech.active_mode, "tts_gpu_budget_mib": speech.gpu_budget_mib,
                       "tts_gpu_peak_mib": speech.gpu_peak_mib, "tts_observed_execution_devices": speech.observed_execution_devices,
                       "tts_model_load_ms": speech.model_load_ms,
                       "tts_voice": speech.speaker, "stt_loaded": hearing.model is not None}.items():
        result["metrics"]["voice." + key] = metric(value, "communication")
    try:
        memory = get_memory()
        result["metrics"]["vault_aims.writer_initialized"] = metric(True, "communication.HostMemory")
        result["metrics"]["vault_aims.running"] = metric(True, "communication.HostMemory")
        result["metrics"]["vault_aims.ledger_entries"] = metric(memory.aims.long_term.total_entries, "communication.HostMemory")
        result["metrics"]["vault_aims.active_sessions"] = metric(len(memory.sessions), "communication.HostMemory")
    except Exception:
        result["metrics"]["vault_aims.running"] = metric(source="communication", reason="Host writer state unavailable")
    try:
        health = language._native_request("/health")
        result["metrics"]["llama_cpp.running"] = metric(health.get("status") == "ok", "llama.cpp /health")
    except Exception:
        result["metrics"]["llama_cpp.running"] = metric(source="llama.cpp", reason="Health probe unavailable")
    try:
        status = loader.load().status()
        for key in ("version", "sha256", "validated", "protected"):
            result["metrics"]["inculcation." + key] = metric(status[key], "communication")
    except Exception as error:
        result["metrics"]["inculcation.validated"] = metric(False, "communication", str(error))
    for key, value in getattr(language, "context_status", foundation_preflight).items():
        result["metrics"]["inculcation.context." + key] = metric(value, "communication")
    return result


@app.post("/conversation")
async def conversation(req: ConversationRequest):
    return await _conversation(req)


async def _conversation(req: ConversationRequest, voice_turn=None):
    def check_cancelled():
        if voice_turn is not None:
            voice_turn.check()
    check_cancelled()
    if not req.text.strip():
        raise HTTPException(422, "Text must not be blank")
    if busy.locked():
        raise HTTPException(429, "Communication is busy; try again after the current reply")
    async with busy:
        memory = get_memory()
        foundation = loader.load()
        activation_id = memory.bind_professional_foundation(foundation)
        session_id = req.session_id or memory.start("orbot-conversation")
        try:
            if req.objective is not None:
                memory.set_objective(session_id, req.objective)
            history = memory.items(session_id)
            recall = memory.recall(session_id, req.text.strip(), limit=3)
            working_context = memory.working_context(session_id)
        except ValueError as error:
            raise HTTPException(409, str(error))
        field_observation = await asyncio.to_thread(observe_field, len(recall["results"]), history)
        check_cancelled()
        integration_evidence = await asyncio.to_thread(retrieve_owner_requested_evidence, req.text.strip())
        check_cancelled()
        inference_started = time.monotonic()
        try:
            reply = await asyncio.to_thread(language.reply, req.text.strip(), history, recall["results"],
                turn_context={"working_memory": working_context,
                              "foundation_sha256": foundation.sha256,
                              "foundation_activation_entry_id": activation_id,
                              "channel": "voice" if voice_turn is not None else "text",
                              "owner_requested_external_evidence": integration_evidence})
            check_cancelled()
            if loader.load().sha256 != foundation.sha256:
                raise FoundationError("Foundation changed during inference; response withheld")
            voice_diagnostics.set("language_ms", round((time.monotonic()-inference_started)*1000))
        except VoiceCancelled:
            raise
        except Exception:
            voice_diagnostics.set("last_error", "Language inference unavailable. Check model connection and context capacity.")
            voice_diagnostics.set("server_stage", "language_failed")
            logging.exception("Local inference failed")
            context = getattr(language, "context_status", {})
            if context.get("fits") is False:
                raise HTTPException(503, {"reason": "Complete professional context does not fit; no education was truncated",
                                          "context": context})
            raise HTTPException(503, "Educated language inference unavailable; no unchecked output released")
        audio, speech_error = None, None
        if req.speak:
            try:
                voice_diagnostics.set("server_stage", "synthesizing")
                synthesis_started = time.monotonic()
                check_cancelled()
                if voice_turn is None:
                    wav = await asyncio.to_thread(speech.synthesize, reply[:1200])
                else:
                    wav = await asyncio.to_thread(speech.synthesize, reply[:1200], voice_turn.cancelled)
                check_cancelled()
                voice_diagnostics.set("tts_generation_ms", round((time.monotonic()-synthesis_started)*1000))
                voice_diagnostics.set("server_stage", "audio_generated_waiting_for_client_playback")
                audio = base64.b64encode(wav).decode("ascii")
            except VoiceCancelled:
                raise
            except Exception as error:
                reason = str(error) if isinstance(error,QwenGpuCapacityError) else "Qwen3-TTS failed. Check local model availability and GPU diagnostics."
                voice_diagnostics.set("last_error", reason)
                voice_diagnostics.set("server_stage", "synthesis_failed")
                voice_diagnostics.increment("synthesis_failures")
                logging.exception("Speech synthesis failed")
                speech_error = reason + "; text reply preserved"
        check_cancelled()
        if loader.load().sha256 != foundation.sha256:
            raise HTTPException(503, "Foundation changed before release; response withheld")
        trace = {"foundation": foundation.status(), "activation_entry_id": activation_id,
                 "sequence": [
                     {"stage": "core_four", "status": "loaded"},
                     {"stage": "professional_inculcation", "status": "loaded"},
                     {"stage": "deployment_and_environment", "status": "volatile_foreground_observation_for_attention_only"},
                     {"stage": "registered_tools", "status": "empty_no_execution_adapter"},
                     {"stage": "owner_requested_system_read", "status": integration_evidence.get("status") if integration_evidence else "not_requested"},
                     {"stage": "session_context", "status": "loaded"},
                     {"stage": "tpc_resolution", "status": "not_integrated"},
                     {"stage": "core4_ral_admission", "status": "not_applied_conversation_only"},
                     {"stage": "reasoning_and_articulation", "status": "completed"},
                     {"stage": "deterministic_response_check", "status": "adapter_checked"},
                     {"stage": "sealed_doctrine", "status": "not_verified"}],
                 "fully_governed": False, "execution_authority": False}
        retention = memory.remember(session_id, {"user": req.text.strip(), "assistant": reply,
            "voice_turn_id": voice_turn.turn_id if voice_turn is not None else None,
            "speech_error": speech_error, "epistemic_field": field_observation,
            "inculcation_sha256": foundation.sha256,
            "audio_wav": audio if req.important or req.priority == "high" else None,
            "recalled_atom_ids": [item["atom_id"] for item in recall["results"]]},
            important=req.important, reason="Operator selected High priority" if req.important or req.priority == "high" else "", priority=req.priority)
        return {"text": reply, "audio_wav": audio, "speech_error": speech_error,
                "session_id": session_id, "memory": retention, "recall": recall,
                "epistemic_field": field_observation, "execution_authority": False,
                "integration_read": ({"source_system": integration_evidence.get("source_system"),
                                      "status": integration_evidence.get("status"),
                                      "result_count": len(integration_evidence.get("items", []))}
                                     if integration_evidence else None),
                "professional_trace": trace, "inference_context": getattr(language,"context_status",{})}
