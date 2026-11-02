"""Deterministic SKG-guided importance review; priority never establishes truth."""
import hashlib
import json

PRIORITIES = ("high", "medium", "low")
CAPACITIES = {"high": 64, "medium": 128, "low": 64}


def fingerprint(payload):
    clean = {k: v for k, v in payload.items() if k not in {"audio_wav", "recalled_atom_ids"}}
    return hashlib.sha256(json.dumps(clean, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def review(knowledge, record, occurrences):
    refs = record["payload"].get("recalled_atom_ids", [])
    refs = refs if isinstance(refs, list) else []
    known = {atom.atom_id for atom in knowledge.by_entry.values()}
    superseded = {edge.target_id for edge in knowledge.aims.skg.active_edges()
                  if edge.relation.value == "supersedes"}
    related = [ref for ref in refs if isinstance(ref, str) and ref in known and ref not in superseded
               and knowledge.aims.vault.get(ref).status.value != "retired"]
    priority = record["priority"]
    if priority == "high":
        return {"retain": True, "priority": "high", "reason": "High priority retained"}
    if priority == "medium" and (related or occurrences >= 2):
        return {"retain": True, "priority": "medium", "reason": "SKG close review: linked context or repeated use"}
    if priority == "low" and related and occurrences >= 3:
        return {"retain": True, "priority": "medium", "reason": "SKG close review: repeated linked context promoted from Low"}
    return {"retain": False, "priority": priority, "reason": "SKG close review: insufficient retention relevance"}
