import sys
import os
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).resolve().parents[1]
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

try:
    from Integration import TPCSystem
except ImportError as e:
    print(f"Failed to import TPCSystem: {e}")
    sys.exit(1)

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Any, Dict, Optional
import time
import io
from results_vault import save_query_result, save_test_run
import tempfile
import numpy as np

app = FastAPI(title="TPC API", version="1.0.0")

_CORS_ORIGINS = [
    f"http://localhost:{p}" for p in range(5173, 5200)
] + [
    f"http://127.0.0.1:{p}" for p in range(5173, 5200)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Singletons ──────────────────────────────────────────────────────────────

_tpc: Optional[TPCSystem] = None
_whisper_model = None
_kokoro_pipeline = None

_COCHLEAR_DIR = parent_dir / "cochlear_processor_3.0"


def get_tpc() -> TPCSystem:
    if _tpc is None:
        raise HTTPException(status_code=503, detail="TPC system not ready")
    return _tpc


def _load_whisper():
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model
    try:
        import whisper
        _whisper_model = whisper.load_model("base")
        print("Whisper model loaded (base)")
        return _whisper_model
    except ImportError:
        raise HTTPException(503, "openai-whisper not installed — run: pip install openai-whisper")


def _load_kokoro():
    global _kokoro_pipeline
    if _kokoro_pipeline is not None:
        return _kokoro_pipeline
    try:
        from kokoro import KPipeline
        _kokoro_pipeline = KPipeline(lang_code="a")   # American English
        print("Kokoro TTS pipeline loaded")
        return _kokoro_pipeline
    except ImportError:
        raise HTTPException(503, "kokoro not installed — run: pip install kokoro soundfile")


# ── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    global _tpc
    try:
        _tpc = TPCSystem()
        _tpc.initialize()
        print("TPC system initialized successfully")
    except Exception as e:
        print(f"Failed to initialize TPC system: {e}")
        _tpc = None


# ── Request models ────────────────────────────────────────────────────────────

class ReasonRequest(BaseModel):
    text: str
    input_type: str = "text"


class SpeakRequest(BaseModel):
    text: str
    voice: str = "af_heart"
    speed: float = 1.0


# ── Basic routes ──────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "TPC API is running"}

@app.get("/test")
def test():
    return {"status": "test endpoint working"}

@app.get("/health")
def health():
    tpc = get_tpc()
    return {"status": "ok", "queries_processed": tpc.query_count}


@app.post("/reason")
def reason(req: ReasonRequest) -> Dict[str, Any]:
    if not req.text.strip():
        raise HTTPException(status_code=422, detail="text must not be empty")
    t0 = time.perf_counter()
    result = get_tpc().process(req.text.strip(), input_type=req.input_type)
    result["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    try:
        save_query_result({**result, "_input_text": req.text.strip()})
    except Exception:
        pass  # vault I/O must never fail a reasoning response
    return result


@app.get("/run-tests")
def run_tests() -> Dict[str, Any]:
    from tests.demo_test import run_all_tests
    results = run_all_tests()
    # Normalise list → dict for vault persistence and consistent schema
    results_dict = {
        r.get("name", str(i)): {**r, "status": "PASS" if r.get("passed") else "FAIL"}
        for i, r in enumerate(results)
    }
    try:
        save_test_run(results_dict)
    except Exception:
        pass  # vault I/O must never fail a test response
    return {"test_results": results_dict}


# ── Audio routes ───────────────────────────────────────────────────────────────

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Transcribe uploaded audio using Whisper, then refine with
    Cochlear 3.0 perceptual correction.

    Accepts: WAV / MP3 / M4A / OGG / FLAC
    Returns: { transcript, cochlear, duration_ms }
    """
    t0 = time.perf_counter()
    whisper_model = _load_whisper()

    suffix = Path(file.filename or "audio.wav").suffix or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # 1. Whisper STT
        raw = whisper_model.transcribe(tmp_path)
        raw_transcript: str = raw["text"].strip()

        # 2. Cochlear 3.0 perceptual correction (optional; degrades gracefully)
        cochlear_report = _run_cochlear_correction(tmp_path, raw_transcript)
        corrected = cochlear_report.get("corrected_transcript", raw_transcript)

        return {
            "transcript": corrected,
            "cochlear": cochlear_report,
            "duration_ms": round((time.perf_counter() - t0) * 1000, 1),
        }
    finally:
        _safe_unlink(tmp_path)


@app.post("/reason-audio")
async def reason_audio(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Full voice-to-reasoning pipeline:
      Whisper STT → Cochlear 3.0 correction → TPC tribunal → result dict
    """
    t0 = time.perf_counter()
    whisper_model = _load_whisper()
    tpc = get_tpc()

    suffix = Path(file.filename or "audio.wav").suffix or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # 1. Whisper STT
        raw = whisper_model.transcribe(tmp_path)
        raw_transcript: str = raw["text"].strip()

        # 2. Cochlear 3.0 perceptual correction
        cochlear_report = _run_cochlear_correction(tmp_path, raw_transcript)
        corrected = cochlear_report.get("corrected_transcript", raw_transcript)

        if not corrected:
            raise HTTPException(422, "Transcription produced empty text")

        # 3. TPC reasoning pipeline
        result = tpc.process(corrected, input_type="text")
        result["transcript"] = corrected
        result["cochlear"] = cochlear_report
        result["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        return result
    finally:
        _safe_unlink(tmp_path)


@app.post("/speak")
def speak(req: SpeakRequest) -> StreamingResponse:
    """
    Convert text to speech via Kokoro TTS.
    Returns: audio/wav stream
    """
    if not req.text.strip():
        raise HTTPException(422, "text must not be empty")

    pipeline = _load_kokoro()

    try:
        import soundfile as sf
    except ImportError:
        raise HTTPException(503, "soundfile not installed — run: pip install soundfile")

    chunks = []
    sample_rate = 24000
    for _gs, _ps, audio in pipeline(req.text.strip(), voice=req.voice, speed=req.speed):
        if audio is not None and len(audio) > 0:
            chunks.append(np.asarray(audio, dtype=np.float32))

    if not chunks:
        raise HTTPException(500, "Kokoro TTS produced no audio")

    combined = np.concatenate(chunks)
    buf = io.BytesIO()
    sf.write(buf, combined, sample_rate, format="WAV")
    buf.seek(0)
    return StreamingResponse(buf, media_type="audio/wav",
                             headers={"Content-Disposition": "inline; filename=tpc_response.wav"})


# ── Helpers ───────────────────────────────────────────────────────────────────

def _run_cochlear_correction(audio_path: str, raw_transcript: str) -> Dict[str, Any]:
    """
    Route audio through Cochlear Processor 3.0 for perceptual correction.
    Returns a report dict. Gracefully degrades if cochlear deps missing.
    """
    try:
        cochlear_dir_str = str(_COCHLEAR_DIR)
        if cochlear_dir_str not in sys.path:
            sys.path.insert(0, cochlear_dir_str)

        from cochlear_processor_v3 import CochlearProcessorV3  # noqa: PLC0415
        proc = CochlearProcessorV3(skg_path=str(_COCHLEAR_DIR / "hearing_skg.json"))
        trace = proc.process_audio_human_like(
            audio_path, context={"topic": "tpc_reasoning", "text": raw_transcript}
        )
        final_transcript = trace.get("final_transcript", raw_transcript)
        perc_report = trace.get("perceptual_report", {})
        return {
            "available": True,
            "raw_transcript": raw_transcript,
            "corrected_transcript": final_transcript,
            "corrections_made": len(trace.get("corrections", [])),
            "perceptual_confidence": round(float(perc_report.get("confidence_factor", 1.0)), 4),
        }
    except Exception as exc:
        return {
            "available": False,
            "raw_transcript": raw_transcript,
            "corrected_transcript": raw_transcript,
            "error": str(exc),
        }


def _safe_unlink(path: str) -> None:
    try:
        os.unlink(path)
    except OSError:
        pass
