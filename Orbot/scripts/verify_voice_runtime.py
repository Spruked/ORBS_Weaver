"""Live configured-service probe. This is not a microphone or playback test."""
import base64
import hashlib
import io
import json
import sys
import time
import wave
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
TOKEN = ROOT.parent / "orbs_vault_system/.local/host-memory.token"

def call(path, payload=None, authenticated=False):
    headers={"Content-Type":"application/json"}
    if authenticated: headers["Authorization"]="Bearer "+TOKEN.read_text().strip()
    req=Request("http://127.0.0.1:16521"+path, data=None if payload is None else json.dumps(payload).encode(),headers=headers)
    with urlopen(req,timeout=300) as response: return json.load(response)

def wav_info(data):
    with wave.open(io.BytesIO(data),"rb") as wav:
        return {"rate":wav.getframerate(),"channels":wav.getnchannels(),"seconds":round(wav.getnframes()/wav.getframerate(),3),"sha256":hashlib.sha256(data).hexdigest()}

def main():
    report={"tested_at":datetime.now(timezone.utc).isoformat(),"fixture":"Hello Orbot. Reply briefly.","microphone":"not tested by this service probe","playback":"not tested by this service probe"}
    active=call("/sessions/embodiment",authenticated=True)["session_id"]
    session=None
    try:
        start=time.monotonic()
        fixture=call("/voice/synthesize",{"text":report["fixture"]},True)
        wav=base64.b64decode(fixture["audio_wav"])
        report["fixture_synthesis"]={"provider":fixture["provider"],"elapsed_ms":round((time.monotonic()-start)*1000),**wav_info(wav)}
        (ROOT/".local/voice_probe_fixture.wav").write_bytes(wav)
        session=call("/sessions",{})["session_id"]
        start=time.monotonic()
        result=call("/voice/input",{"session_id":session,"turn_id":"configured-services-probe","audio_wav":fixture["audio_wav"]})
        report["elapsed_ms"]=round((time.monotonic()-start)*1000)
        report["hearing"]=result["hearing"]
        report["response_text"]=result["text"]
        report["response_audio"]=wav_info(base64.b64decode(result["audio_wav"])) if result.get("audio_wav") else None
        report["foundation"]=result["professional_trace"]["foundation"]
        report["fully_governed"]=result["professional_trace"]["fully_governed"]
        report["execution_authority"]=result["execution_authority"]
        report["same_conversation_session"]=result["session_id"]==session
        report["service_round_trip_passed"]=bool(report["response_audio"] and report["foundation"]["version"]=="1.3")
        (ROOT/".local/voice_probe_reply.wav").write_bytes(base64.b64decode(result["audio_wav"]))
    except Exception as error:
        report["error"]=str(error)
        if hasattr(error,"read"):report["error_detail"]=error.read().decode()
    finally:
        if session:call("/sessions/end",{"session_id":session})
        report["embodiment_session_preserved"]=call("/sessions/embodiment",authenticated=True)["session_id"]==active
        report["voice_metrics"]={key:value["value"] for key,value in call("/diagnostics")["metrics"].items() if key.startswith("voice.")}
        path=ROOT/"docs/voice_service_acceptance_results.json"
        path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(report,indent=2))
    return 0 if report.get("service_round_trip_passed") else 1

if __name__=="__main__":sys.exit(main())
