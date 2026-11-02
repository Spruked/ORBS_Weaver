"""Own the existing Core-4 implementation; no production permit issuer yet."""
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from .ral_core.ral_core.core4 import evaluate_core4
from pydantic import BaseModel, ConfigDict, Field
from .epistemic_field import EpistemicField
from runtime.shared.diagnostics import RuntimeDiagnostics, metric
from .inculcation import loader

diagnostics = RuntimeDiagnostics("cognition_governance")

epistemic_field = EpistemicField()


class FieldObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    recalled_count: int = Field(ge=0, le=100)
    word_confidence: float = Field(ge=0, le=1, allow_inf_nan=False)

app = FastAPI(title="Orbot Cognition/Governance", docs_url=None, redoc_url=None)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"])


@app.on_event("startup")
def initialize_professional_foundation():
    # Read the same deployment artifact; never open another AIMS writer.
    loader.load()
    epistemic_field.initialize()


@app.get("/health")
def health():
    foundation = loader.load()
    return {"runtime": "cognition_governance", "ready": True,
            "mode": "deterministic-evaluation-only", "core4": ["Kant", "Locke", "Hume", "Spinoza"],
            "execution_authority": False, "permit_authority_ready": False,
            "professional_foundation": foundation.status()}


def evaluate(proposal, world):
    """Internal typed evaluation, never an execution grant or state commit."""
    loader.load()
    return evaluate_core4(proposal, world)


@app.post("/field/observe")
def observe_field(observation: FieldObservation):
    loader.load()
    return epistemic_field.observe(observation.recalled_count, observation.word_confidence)


@app.get("/field/status")
def field_status():
    return epistemic_field.snapshot()


@app.get("/diagnostics")
def runtime_diagnostics():
    result = diagnostics.snapshot()
    snapshot = epistemic_field.snapshot()
    result["metrics"]["field_initialized"] = metric(snapshot["initialized"], diagnostics.name)
    for key, value in snapshot["stats"].items():
        result["metrics"]["field." + key] = metric(value, diagnostics.name)
    result["metrics"]["field.seed"] = metric(source=diagnostics.name,
        reason="Existing field RNG seed was not captured")
    return result
