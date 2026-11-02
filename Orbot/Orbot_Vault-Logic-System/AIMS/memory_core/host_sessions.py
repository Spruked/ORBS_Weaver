"""Session-isolated working memory and explicit, provenance-preserving retention."""
from __future__ import annotations

import json
import secrets
import sqlite3
import threading
import time
import uuid
from pathlib import Path

from .memory_layer import AIMSMemorySystem
from .long_term import EntryType
from .short_term import ShortTermMemory
from .host_knowledge import HostKnowledge
from .host_priority import PRIORITIES, CAPACITIES, fingerprint


class HostMemory:
    def __init__(self, root: Path, idle_seconds: int = 1800):
        self.root = Path(root)
        self.aims = AIMSMemorySystem(self.root, matrix_id="orbot_host")
        self.lock = threading.RLock()
        self.sessions = {}
        self.embodiment_session = None
        self.idle_seconds = idle_seconds
        # A disposable projection. The AIMS immutable ledger remains canonical.
        self.db = sqlite3.connect(self.root / "host_collections.sqlite", check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS collections (name TEXT PRIMARY KEY, payload TEXT, entry_id TEXT)")
        self.rebuild()
        self.knowledge = HostKnowledge(self.aims)
        # Separate from all evictable session/priority caches. Host startup binds
        # an immutable validated snapshot; no conversation API can replace it.
        self._professional_foundation = None
        self._foundation_activation = None

    def bind_professional_foundation(self, foundation):
        with self.lock:
            if (self._professional_foundation is not None and
                    self._professional_foundation.sha256 == foundation.sha256):
                return self._foundation_activation
            previous = self._professional_foundation
            prior_entry = next((item for item in reversed(list(self.aims.long_term.iterate_entries()))
                                if item.content.get("host_kind") == "professional_foundation_activation"), None)
            entry = self.aims.commit(EntryType.SYSTEM_EVENT,
                {"host_kind": "professional_foundation_activation",
                 "artifact": json.loads(foundation.artifact_json),
                 "sha256": foundation.sha256,
                 "previous_sha256": previous.sha256 if previous else
                    (prior_entry.content.get("sha256") if prior_entry else None),
                 "previous_activation_entry_id": prior_entry.entry_id if prior_entry else None},
                metadata={"source": "owner-controlled-inculcation-deployment",
                          "authority_class": "configuration", "version": foundation.version,
                          "retention_reason": "Validated professional foundation activated before cognition",
                          "verification_status": "source_integrity_validated_not_execution_authorization"},
                writer_id="orbot-host")
            # The existing immutable ledger supplies timestamps and durable
            # recovery/provenance. Do not assert the entire education as truth.
            self._professional_foundation = foundation
            self._foundation_activation = entry.entry_id
            return entry.entry_id

    def professional_foundation_status(self):
        with self.lock:
            if self._professional_foundation is None:
                return {"validated": False, "activation_entry_id": None}
            return {**self._professional_foundation.status(),
                    "activation_entry_id": self._foundation_activation}

    def set_objective(self, session: str, objective: str):
        with self.lock:
            self._session(session)["objective"] = objective

    def working_context(self, session: str):
        with self.lock:
            state = self._session(session)
            return {"objective": state.get("objective"), "source": state["source"],
                    "verification_status": "operator_provided_not_independently_verified"}

    def rebuild(self):
        with self.lock, self.db:
            self.db.execute("DELETE FROM collections")
            for entry in self.aims.long_term.iterate_entries():
                data = entry.content
                if data.get("host_kind") == "collection":
                    self.db.execute("INSERT OR REPLACE INTO collections VALUES (?,?,?)",
                                    (data["name"], json.dumps(data["payload"]), entry.entry_id))

    def start(self, source: str) -> str:
        with self.lock:
            self.expire()
            if len(self.sessions) >= 64:
                raise ValueError("Too many active sessions")
            session = secrets.token_urlsafe(32)
            self.sessions[session] = {"source": source, "last": time.monotonic(),
                "caches": {name: ShortTermMemory(capacity=CAPACITIES[name]) for name in PRIORITIES},
                "retrievals": [], "occurrences": {}, "retained_records": {}, "closing": False,
                "close_review": {"saved": 0, "pruned": 0, "duplicates": 0}}
            return session

    def start_embodiment(self):
        """One runtime-owned active embodiment session, independent of windows."""
        with self.lock:
            if self.embodiment_session not in self.sessions:
                self.embodiment_session = self.start("orbot-embodiment")
            return self.embodiment_session

    def expire(self):
        with self.lock:
            now = time.monotonic()
            for session in list(self.sessions):
                if session == self.embodiment_session:
                    continue
                if now - self.sessions[session]["last"] > self.idle_seconds:
                    self.end(session, expired=True)

    def _session(self, session: str):
        self.expire()
        if session not in self.sessions:
            raise ValueError("Session expired or closed; start a new session")
        state = self.sessions[session]
        if state["closing"]:
            raise ValueError("Session is closing; retry session end")
        state["last"] = time.monotonic()
        return state

    def remember(self, session: str, payload: dict, important: bool = False, reason: str = "", priority: str | None = None):
        with self.lock:
            state = self._session(session)
            priority = "high" if important else (priority or "low")
            if priority not in PRIORITIES:
                raise ValueError("Priority must be high, medium, or low")
            if priority == "high" and not reason.strip():
                raise ValueError("Long-term retention requires a reason")
            key = fingerprint(payload)
            if key not in state["occurrences"] and len(state["occurrences"]) >= 1024:
                state["occurrences"].pop(next(iter(state["occurrences"])))
            state["occurrences"][key] = state["occurrences"].get(key, 0) + 1
            cache = state["caches"][priority]
            # Review before capacity eviction; never silently discard a pending
            # high-priority write or skip the closing rules for Medium/Low.
            if len(cache.all_items()) >= cache.capacity:
                victim = min(cache.all_items(), key=lambda item: (item.vivacity, item.last_touched))
                self._review_item(session, state, victim.content)
                cache.remove(victim.item_id)
            record = {"payload": payload, "priority": priority, "fingerprint": key,
                      "reason": reason, "entry_id": None, "atom_id": None}
            item = cache.put(record)
            if priority == "high":
                self._retain(session, state, record, priority, reason)
            return {"item_id": item.item_id, "priority": priority, "retained": record["entry_id"] is not None,
                    "entry_id": record["entry_id"], "atom_id": record["atom_id"]}

    def _retain(self, session, state, record, priority, reason):
        previous = state["retained_records"].get(record["fingerprint"])
        if not record["entry_id"] and previous and PRIORITIES.index(previous["priority"]) <= PRIORITIES.index(priority):
            record["entry_id"], record["atom_id"] = previous["entry_id"], previous["atom_id"]
            record["retained_priority"] = previous["priority"]
            record["duplicate_reuse"] = True
            state["close_review"]["duplicates"] += 1
            return
        if record["entry_id"] is None:
            entry = self.aims.commit(EntryType.INTERACTION,
                {"host_kind": "retained_session_item", "payload": record["payload"]},
                metadata={"source": state["source"], "session_id": session,
                          "retention_reason": reason, "priority": priority,
                          "authority_class": "assertion"}, writer_id="orbot-host")
            record["entry_id"] = entry.entry_id
        else:
            entry = self.aims.long_term.read_entry(entry_id=record["entry_id"])
        priority = entry.metadata.get("priority", priority)
        record["retained_priority"] = priority
        if record["atom_id"] is None:
            record["atom_id"] = self.knowledge.record(entry).atom_id
        record["retained_priority"] = priority
        state["retained_records"][record["fingerprint"]] = {"entry_id": record["entry_id"], "atom_id": record["atom_id"], "priority": priority}
        if len(state["retained_records"]) > 1024:
            state["retained_records"].pop(next(iter(state["retained_records"])))

    def _review_item(self, session, state, record):
        if record.get("review_complete"):
            return
        if record["entry_id"]:
            self._retain(session, state, record, record.get("retained_priority", record["priority"]), record["reason"])
            if record["priority"] != "high" and not record.get("counted_saved") and not record.get("duplicate_reuse"):
                state["close_review"]["saved"] += 1
                record["counted_saved"] = True
            record["review_complete"] = True
            return
        decision = self.knowledge.review_priority(record, state["occurrences"].get(record["fingerprint"], 1))
        if decision["retain"]:
            self._retain(session, state, record, decision["priority"], decision["reason"])
            if not record.get("duplicate_reuse"):
                state["close_review"]["saved"] += 1
            record["counted_saved"] = True
        else:
            state["close_review"]["pruned"] += 1
        record["review_complete"] = True

    def recall(self, session: str, query: str, limit: int = 5):
        with self.lock:
            state = self._session(session)
            results = self.knowledge.recall(query, max(1, min(limit, 10)))
            receipt = {"retrieval_id": str(uuid.uuid4()), "query": query, "results": results}
            state["retrievals"] = [*state["retrievals"][-31:], receipt]
            # Ordinary questions and receipts stay volatile with their session.
            return receipt

    def knowledge_status(self):
        with self.lock:
            counts = {name: 0 for name in PRIORITIES}
            superseded = {edge.target_id for edge in self.aims.skg.active_edges() if edge.relation.value == "supersedes"}
            for entry_id, atom in self.knowledge.by_entry.items():
                if atom.atom_id not in superseded and atom.status.value != "retired":
                    entry = self.aims.long_term.read_entry(entry_id=entry_id)
                    counts[entry.metadata.get("priority", "high")] += 1
            return {"vault": self.aims.vault.stats(), "skg": self.aims.skg.stats(),
                    "host_atoms": len(self.knowledge.by_entry), "persistent": True,
                    "session_queries_persisted": False,
                    "cache_priorities": list(PRIORITIES), "system_caches": counts}

    def items(self, session: str):
        with self.lock:
            state = self._session(session)
            items = [item for cache in state["caches"].values() for item in cache.all_items()]
            return [item.content["payload"] for item in sorted(items, key=lambda item: item.created_at)]

    def cache_status(self, session):
        with self.lock:
            state = self._session(session)
            return {name: {"count": len(state["caches"][name].all_items()), "capacity": state["caches"][name].capacity}
                    for name in PRIORITIES}

    def end(self, session: str, expired: bool = False):
        with self.lock:
            # Do not call _session here: expiry itself invokes closing review.
            if session not in self.sessions:
                raise ValueError("Session expired or closed; start a new session")
            state = self.sessions[session]
            state["closing"] = True
            seen = set()
            for priority in PRIORITIES:
                for item in state["caches"][priority].all_items():
                    record = item.content
                    if record.get("review_complete"):
                        seen.add(record["fingerprint"])
                        continue
                    if record["fingerprint"] in seen and not record["entry_id"]:
                        state["close_review"]["duplicates"] += 1
                        record["review_complete"] = True
                        continue
                    self._review_item(session, state, record)
                    seen.add(record["fingerprint"])
            report = {**state["close_review"], "expired": expired,
                      "retained_high": len({item.content["entry_id"] for item in state["caches"]["high"].all_items() if item.content["entry_id"]})}
            # All durable writes and graph updates above must succeed before purge.
            del self.sessions[session]
            if self.embodiment_session == session:
                self.embodiment_session = None
            return report

    def close_all(self):
        with self.lock:
            return [self.end(session) for session in list(self.sessions)]

    def collection(self, name: str, default=None):
        with self.lock:
            row = self.db.execute("SELECT payload FROM collections WHERE name=?", (name,)).fetchone()
            return json.loads(row[0]) if row else default

    def collection_revision(self, name: str):
        with self.lock:
            row = self.db.execute("SELECT entry_id FROM collections WHERE name=?", (name,)).fetchone()
            return row[0] if row else None

    def save_collection(self, name: str, payload, source: str, reason: str, expected_entry_id=None):
        with self.lock:
            if not reason.strip():
                raise ValueError("Retention reason required")
            if self.collection_revision(name) != expected_entry_id:
                raise ValueError("Collection changed; reload before saving")
            entry = self.aims.commit(EntryType.SYSTEM_EVENT,
                {"host_kind": "collection", "name": name, "payload": payload},
                metadata={"source": source, "retention_reason": reason,
                          "authority_class": "configuration", "priority": "high"}, writer_id="dock-station")
            atom = self.knowledge.record(entry)
            with self.db:
                self.db.execute("INSERT OR REPLACE INTO collections VALUES (?,?,?)",
                                (name, json.dumps(payload), entry.entry_id))
            return {"entry_id": entry.entry_id, "retained": True, "atom_id": atom.atom_id}
