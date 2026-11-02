"""Owner-deployed professional education. Integrity is not execution authority.

Only the offline CLI writes compiled/activation files. Runtime users, session
memory and model output have no update API. The filesystem deployment boundary
is the existing owner boundary; a digest is not a credential or a signature.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import threading

ROOT = Path(__file__).resolve().parents[2] / "inculcation"
DOCUMENT_ID = "DESKTOP-ORB-INCULCATION-001"
TITLES = (
    "Who am I?", "Where am I?", "Why am I here?", "What is my job?",
    "Who do I serve?", "What should I know?", "What tools do I have?",
    "How do I do my job well?", "How do I understand my environment?",
    "How do I know I succeeded?", "How do I improve?", "Examples",
)
SOURCE = "Desktop_ORB_Professional_Inculcation_v1.3.md"


class FoundationError(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def read_local(root: Path, name: str) -> bytes:
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise FoundationError("Reference escapes the foundation directory")
    try:
        return path.read_bytes()
    except OSError as error:
        raise FoundationError("Required foundation file unavailable: " + name) from error


def read_json(root: Path, name: str):
    try:
        return json.loads(read_local(root, name))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise FoundationError("Invalid foundation JSON: " + name) from error


def compile_foundation(root: Path = ROOT) -> dict:
    """Lossless section compilation against the recorded source set."""
    root = Path(root)
    sources = read_json(root, "sources.json")
    required = {"references/Desktop_ORB_Professional_Inculcation_v1.1.md",
                "references/Professional_Inculcation_Canonical_Outline_v1.0.txt",
                "references/ORB_Inculcation_Harness_Outline.txt",
                "references/ORBS_Foundational_Architecture_Standard.txt",
                "references/metadata.json", "Core_Four_Baseline.txt"}
    if set(sources) != required:
        raise FoundationError("Required reference source set is incomplete")
    for name, expected in sources.items():
        if digest(read_local(root, name)) != expected:
            raise FoundationError("Source integrity mismatch: " + name)
    baseline = read_local(root, "Core_Four_Baseline.txt").decode("utf-8").strip()
    standard = read_local(root, "references/ORBS_Foundational_Architecture_Standard.txt").decode("utf-8")
    start = standard.index("1. Ground reasoning in evidence")
    stop = standard.index("3. INVARIANCE OF THE BASELINE")
    if baseline != standard[start:stop].strip():
        raise FoundationError("Core Four differs from the complete canonical baseline")
    source_bytes = read_local(root, SOURCE)
    text = source_bytes.decode("utf-8").replace("\r\n", "\n")
    version_match = re.search(r"^Version: (\d+\.\d+)$", text, re.M)
    if not version_match or "Document ID: " + DOCUMENT_ID not in text:
        raise FoundationError("Document identity/version missing")
    matches = list(re.finditer(r"^## (\d+)\. (.+)$", text, re.M))
    if [(int(m[1]), m[2]) for m in matches] != list(enumerate(TITLES, 1)):
        raise FoundationError("All twelve ordered training sections are required")
    sections = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():end].strip()
        if len(body.split()) < 40:
            raise FoundationError("Training content missing: " + match[2])
        sections.append({"order": index + 1, "title": match[2], "text": body})
    return {
        "schema_version": 1, "document_id": DOCUMENT_ID, "version": version_match[1],
        "source_document": SOURCE, "source_sha256": digest(source_bytes),
        "source_preamble": text[:matches[0].start()].strip(),
        "sources": sources, "core_four": {"source": "Core_Four_Baseline.txt", "text": baseline},
        "training_sections": sections,
        "initialization": {"required_before_interaction": True,
                           "order": ["complete_core_four", "complete_professional_inculcation",
                                     "deployment_and_verified_environment", "registered_tools", "session_context"]},
        "retention": {"partition": "protected_read_only_professional_foundation",
                      "session_purge": False, "conversation_updates": False,
                      "durable_record": "existing_AIMS_host_writer", "grants_execution_authority": False},
        "restoration": {"submit_complete_prefix_on_every_context": True,
                        "kv_reuse": "opportunistic_shared_llama_cpp_cache_prompt",
                        "on_eviction_restart_or_truncation": "revalidate_and_restore_before_inference",
                        "insufficient_context": "fail_closed_without_truncating_education"},
        "reload": {"requires": "owner_controlled_offline_deployment",
                   "validate_version_integrity_and_previous_activation": True,
                   "on_change": "replace_immutable_snapshot_invalidate_prefix_and_record_AIMS_activation"},
    }


@dataclass(frozen=True)
class Foundation:
    document_id: str
    version: str
    sha256: str
    artifact_json: str
    prefix: str

    def status(self):
        return {"document_id": self.document_id, "version": self.version,
                "sha256": self.sha256, "sections": 12, "validated": True,
                "protected": True, "execution_authority": False}


class FoundationLoader:
    def __init__(self, root: Path = ROOT):
        self.root = Path(root)
        self._snapshot = None
        self._lock = threading.RLock()
        self.loads = 0

    def load(self) -> Foundation:
        # Validate disk inputs even on a warm application cache. An unauthorized
        # edit must not silently retain an apparently healthy cached identity.
        with self._lock:
            expected = compile_foundation(self.root)
            data = read_local(self.root, "inculcation.compiled.json")
            activation = read_json(self.root, "activation.json")
            identity = digest(data)
            if data != canonical(expected):
                raise FoundationError("Compiled training does not match its complete sources")
            if activation.get("sha256") != identity or activation.get("version") != expected["version"]:
                raise FoundationError("Compiled version has not been activated by owner deployment")
            if activation.get("document_id") != DOCUMENT_ID:
                raise FoundationError("Activation document identity mismatch")
            if self._snapshot is None or self._snapshot.sha256 != identity:
                professional = expected["source_preamble"] + "\n\n" + "\n\n".join(
                    f"## {s['order']}. {s['title']}\n\n{s['text']}" for s in expected["training_sections"])
                self._snapshot = Foundation(DOCUMENT_ID, expected["version"], identity, data.decode("utf-8"),
                    "UNIVERSAL CORE FOUR — COMPLETE INVARIANT BASELINE\n\n" + expected["core_four"]["text"] +
                    "\n\nDESKTOP PROFESSIONAL EDUCATION — COMPLETE\n\n" + professional)
                self.loads += 1
            return self._snapshot


loader = FoundationLoader()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("compile", "activate", "verify"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--approve-sha256")
    parser.add_argument("--expected-previous", help="previous digest, or 'none' for first deployment")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.operation == "compile":
        data = canonical(compile_foundation(root))
        (root / "inculcation.compiled.json").write_bytes(data)
        print(json.dumps({"candidate_sha256": digest(data), "activated": False}))
    elif args.operation == "activate":
        data = read_local(root, "inculcation.compiled.json")
        expected = compile_foundation(root)
        if data != canonical(expected) or args.approve_sha256 != digest(data):
            raise FoundationError("Explicit approval of the exact validated candidate digest is required")
        path = root / "activation.json"
        previous = json.loads(path.read_bytes()) if path.exists() else None
        if args.expected_previous != (previous["sha256"] if previous else "none"):
            raise FoundationError("Previous activation changed or was not explicitly supplied")
        if previous and previous["sha256"] != digest(data):
            old_version = tuple(map(int, previous["version"].split(".")))
            if tuple(map(int, expected["version"].split("."))) <= old_version:
                raise FoundationError("A replacement must advance the version")
        activation = {"document_id": DOCUMENT_ID, "version": expected["version"], "sha256": digest(data),
                      "previous_sha256": previous["sha256"] if previous else None,
                      "activated_at": datetime.now(timezone.utc).isoformat(),
                      "mechanism": "owner_controlled_offline_deployment"}
        temporary = root / "activation.json.tmp"
        temporary.write_bytes(canonical(activation))
        temporary.replace(path)
        print(json.dumps(activation))
    else:
        print(json.dumps(FoundationLoader(root).load().status()))


if __name__ == "__main__":
    main()
