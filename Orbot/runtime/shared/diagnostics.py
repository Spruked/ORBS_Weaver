"""Read-only producer measurements. No inferred readiness or authority."""
import os
import time
import uuid
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


def metric(value=None, source="unknown", reason=None):
    stamp = now()
    return {"value": value, "status": "unknown" if value is None else "measured",
            "source": source, "measured_at": stamp if value is not None else None,
            "received_at": stamp, "reason": reason}


class RuntimeDiagnostics:
    def __init__(self, name):
        self.name = name
        self.instance = str(uuid.uuid4())
        self.started_at = now()
        self.started = time.monotonic()

    def snapshot(self):
        values = {"running": True, "pid": os.getpid(),
                  "uptime_seconds": time.monotonic() - self.started,
                  "instance_started_at": self.started_at, "heartbeat_at": now()}
        result = {key: metric(value, self.name) for key, value in values.items()}
        for key in ("schemas_validated", "policy_validated", "grants_validated",
                    "adapters_validated", "last_restart_at", "errors_last_hour",
                    "errors_last_day", "crashes_last_hour", "crashes_last_day"):
            result[key] = metric(source=self.name, reason="Measurement not implemented")
        return {"schema_version": 1, "runtime": self.name,
                "process_instance_id": self.instance, "metrics": result}
