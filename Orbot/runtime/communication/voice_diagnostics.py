"""Volatile stage measurements; no recordings/transcripts or inferred consent."""
from datetime import datetime, timezone
from threading import RLock


class VoiceDiagnostics:
    def __init__(self):
        self.lock = RLock()
        self.values = {}

    def set(self, key, value, source="communication_voice"):
        with self.lock:
            self.values[key] = {"value": value, "status": "measured", "source": source,
                                "measured_at": datetime.now(timezone.utc).isoformat(), "reason": None}

    def increment(self, key):
        with self.lock:
            self.set(key, self.values.get(key, {}).get("value", 0) + 1)

    def snapshot(self):
        with self.lock:
            result = {"voice." + key: dict(value) for key, value in self.values.items()}
            if "voice.server_stage" in result:
                result["voice.server_stage"]["measured_at"] = datetime.now(timezone.utc).isoformat()
            return result


voice_diagnostics = VoiceDiagnostics()
