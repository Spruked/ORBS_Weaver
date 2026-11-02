"""Vault-backed host memory atoms and scoped, non-authoritative SKG recall."""
from __future__ import annotations

import json
import re

from .skg.types import Relation


class HostKnowledge:
    def review_priority(self, record, occurrences):
        from .host_priority import review
        return review(self, record, occurrences)

    def __init__(self, aims):
        self.aims = aims
        self.by_entry = {}
        self._edges = set()
        self.reconcile()

    def reconcile(self):
        self.by_entry = {atom.metadata["host_entry_id"]: atom for atom in self.aims.vault.all_atoms()
                         if atom.metadata.get("host_entry_id")}
        self._edges = {(edge.source_id, edge.target_id, edge.relation) for edge in self.aims.skg.all_edges()}
        previous_collection = {}
        previous_session = {}
        for entry in self.aims.long_term.iterate_entries():
            kind = entry.content.get("host_kind")
            if kind not in {"collection", "retained_session_item"}:
                continue
            atom = self.index(entry)
            self.link_context(entry, atom)
            if kind == "collection":
                key = entry.content["name"]
                if key in previous_collection:
                    self.link(atom.atom_id, previous_collection[key], Relation.SUPERSEDES)
                previous_collection[key] = atom.atom_id
            else:
                key = entry.metadata.get("session_id")
                if key and key in previous_session:
                    self.link(previous_session[key], atom.atom_id, Relation.TEMPORALLY_PRECEDES)
                if key:
                    previous_session[key] = atom.atom_id
        self.aims.indexes.rebuild(self.aims.vault)
        self.previous_collection = previous_collection
        self.previous_session = previous_session

    def record(self, entry):
        atom = self.index(entry)
        if entry.content["host_kind"] == "collection":
            key = entry.content["name"]
            previous = self.previous_collection.get(key)
            if previous:
                self.link(atom.atom_id, previous, Relation.SUPERSEDES)
            self.previous_collection[key] = atom.atom_id
        else:
            key = entry.metadata.get("session_id")
            previous = self.previous_session.get(key)
            if previous:
                self.link(previous, atom.atom_id, Relation.TEMPORALLY_PRECEDES)
            if key:
                self.previous_session[key] = atom.atom_id
            self.link_context(entry, atom)
        return atom

    def link_context(self, entry, atom):
        payload = entry.content.get("payload", {})
        if not isinstance(payload, dict):
            return
        references = payload.get("recalled_atom_ids", [])
        if not isinstance(references, list):
            return
        known_ids = {item.atom_id for item in self.by_entry.values()}
        for referenced in references[:10]:
            if isinstance(referenced, str) and referenced in known_ids:
                self.link(atom.atom_id, referenced, Relation.CONTEXT_DEPENDENT)

    @staticmethod
    def summary(entry):
        data = entry.content
        if data.get("host_kind") == "retained_session_item":
            payload = data["payload"]
            if isinstance(payload.get("user"), str):
                text = "Operator said: " + payload["user"][:2500]
                if isinstance(payload.get("assistant"), str):
                    text += "\nOrbot replied (unverified): " + payload["assistant"][:1200]
                return text
            # Only describe the retained observation; never infer its truth.
            return "Retained observation: " + HostKnowledge.clean_text(payload)[:3000]
        return "Saved configuration " + data["name"] + ": " + HostKnowledge.clean_text(data["payload"])[:3000]

    @staticmethod
    def clean_text(value):
        def clean(item):
            if isinstance(item, dict):
                return {k: clean(v) for k, v in item.items() if not any(
                    term in k.lower() for term in ("password", "secret", "token", "api_key", "audio", "base64", "texture_url"))}
            if isinstance(item, list):
                return [clean(v) for v in item[:50]]
            return item
        return json.dumps(clean(value), ensure_ascii=False, default=str)

    def index(self, entry):
        atom = self.by_entry.get(entry.entry_id)
        if atom is None:
            atom = self.aims.derive_aposteriori(self.summary(entry), [entry],
                metadata={"host_entry_id": entry.entry_id, "host_kind": entry.content["host_kind"],
                          "collection": entry.content.get("name"),
                          "authority_class": "assertion", "source": entry.metadata.get("source", "host"),
                          "retention_reason": entry.metadata.get("retention_reason", "")},
                initial_confidence=0.5)
            self.by_entry[entry.entry_id] = atom
        self.aims.indexes.upsert(atom)
        return atom

    def link(self, first, second, relation):
        key = (first, second, relation)
        if key not in self._edges and first != second:
            self.aims.link(first, second, relation)
            self._edges.add(key)

    def recall(self, query: str, limit: int = 5):
        # Token-wise lookup avoids requiring every word in a natural-language
        # question to occur in the saved assertion. No semantic/truth inference.
        stop = {"the", "and", "that", "this", "what", "with", "have", "you", "your", "did", "does", "about", "remember", "please", "said", "was", "are", "for"}
        tokens = list(dict.fromkeys(word.casefold() for word in re.findall(r"[^\W_]+", query)
                                   if len(word) > 2 and word.casefold() not in stop))[:12]
        matches = {}
        superseded = {edge.target_id for edge in self.aims.skg.active_edges() if edge.relation is Relation.SUPERSEDES}
        for token in tokens:
            results = self.aims.indexes.search(self.aims.vault, token, limit=100,
                skg_weight_for=self.aims.skg.relevance_weight, include_probation=True)
            for result in results:
                if not result["metadata"].get("host_entry_id") or result["atom_id"] in superseded:
                    continue
                current, count = matches.get(result["atom_id"], (result, 0))
                matches[result["atom_id"]] = (current, count + 1)
        ordered = sorted(matches.values(), key=lambda item: (-item[1], -item[0]["relevance_score"], item[0]["atom_id"]))
        output = []
        for result, count in ordered[:limit]:
            edges = [edge.to_dict() for edge in self.aims.skg.active_edges()
                     if result["atom_id"] in {edge.source_id, edge.target_id}]
            output.append({"atom_id": result["atom_id"], "statement": result["statement"],
                "status": result["status"], "confidence": result["confidence"],
                "verified": False, "authority_class": "assertion",
                "source_entry_ids": result["derived_from"], "source": result["metadata"].get("source"),
                "priority": self.aims.long_term.read_entry(entry_id=result["derived_from"][0]).metadata.get("priority", "high"),
                "matched_terms": count, "skg_weight": result["skg_weight"], "relationships": edges})
        return output
