"""Loopback advisory client; communication never owns a second field instance."""
import json
from urllib.request import Request, urlopen


def observe_field(recalled_count, history):
    confidence = 0.0
    for item in reversed(history):
        hearing = item.get("hearing", {})
        scores = hearing.get("word_confidences", [])
        if scores:
            confidence = sum(float(score) for score in scores) / len(scores)
            break
    request = Request("http://127.0.0.1:16524/field/observe",
                      data=json.dumps({"recalled_count": recalled_count,
                                       "word_confidence": confidence}).encode(),
                      headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=10) as response:
            return json.load(response)
    except (OSError, ValueError):
        return {"available": False, "advisory_only": True,
                "verified": False, "execution_authority": False}
