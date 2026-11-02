"""Limited deterministic response checks, NOT sealed Doctrine or semantic proof.

No tool is registered in Communication. Tool requests and narration of external
execution therefore cannot be released here. Future adapters must supply real
event records and an independently verified governing release contract.
"""
import re


class ConformanceError(ValueError):
    def __init__(self, label, reason):
        self.label = label
        super().__init__(reason)


def validate_tool_correspondence(claim, events):
    """An evaluation helper for real events; not an authorization issuer."""
    event = next((e for e in events if e.get("event_id") == claim.get("event_id")), None)
    if event is None or any(claim.get(k) != event.get(k) for k in ("tool_id", "operation", "target", "status")):
        raise ConformanceError("FALSE_TOOL_NARRATION", "Tool claim does not match an event")
    if event.get("status") != "verified" or not event.get("authorization_reference") or not event.get("evidence_reference"):
        raise ConformanceError("FALSE_TOOL_NARRATION", "Tool completion lacks authorized verified evidence")


def validate_response(value):
    if not isinstance(value, dict) or set(value) != {"text", "requested_tool", "tool_claims"}:
        raise ConformanceError("DESKTOP_RESPONSE_CONTRACT", "Structured response is required")
    if value["requested_tool"] is not None:
        raise ConformanceError("DESKTOP_UNREGISTERED_TOOL", "No executable tool is registered")
    if value["tool_claims"] != []:
        raise ConformanceError("FALSE_TOOL_NARRATION", "No tool event source is connected")
    text = value["text"]
    if not isinstance(text, str) or not text.strip():
        raise ConformanceError("DESKTOP_RESPONSE_CONTRACT", "Nonempty text is required")
    # Deliberately conservative examples. These catch explicit first-person
    # execution claims, not all possible paraphrases or unsupported factuality.
    pattern = r"\bI(?:'ve| have| successfully)?\s+(?:sent|deleted|installed|executed|clicked|opened|moved|saved|updated|verified|searched|read your|read the|checked your|checked the)\b"
    if re.search(pattern, text, re.I):
        raise ConformanceError("FALSE_TOOL_NARRATION", "Execution narration has no matching event")
    return text.strip()


RESPONSE_SCHEMA = {
    "type": "object", "properties": {
        "text": {"type": "string"}, "requested_tool": {"type": "null"},
        "tool_claims": {"type": "array", "maxItems": 0, "items": {"type": "object"}},
    }, "required": ["text", "requested_tool", "tool_claims"], "additionalProperties": False,
}
