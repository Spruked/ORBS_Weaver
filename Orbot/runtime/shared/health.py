"""Local status only; these endpoints cannot authorize actions."""
import json
from urllib.request import urlopen

PORTS = {"communication": 16521, "cognition_governance": 16524, "motion": 16525}


def peer_status(name):
    try:
        with urlopen(f"http://127.0.0.1:{PORTS[name]}/health", timeout=1) as response:
            return json.load(response)
    except Exception:
        return {"runtime": name, "ready": False}
