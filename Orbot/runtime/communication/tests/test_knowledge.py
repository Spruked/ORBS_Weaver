import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runtime.communication.memory import HostMemory


class KnowledgeWiringTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.memory = HostMemory(Path(self.temp.name))

    def tearDown(self):
        self.memory.db.close()
        self.temp.cleanup()

    def test_retained_memory_has_vault_atom_and_cross_session_recall(self):
        first = self.memory.start("orb")
        saved = self.memory.remember(first, {"user": "The workshop project is Blue Lantern", "assistant": "Noted"}, True, "Owner selected")
        self.memory.end(first)
        second = self.memory.start("orb")
        recall = self.memory.recall(second, "What was the workshop project?")
        self.assertEqual(recall["results"][0]["atom_id"], saved["atom_id"])
        self.assertEqual(recall["results"][0]["source_entry_ids"], [saved["entry_id"]])
        self.assertEqual(recall["results"][0]["status"], "probation")
        self.assertFalse(recall["results"][0]["verified"])
        self.assertEqual(self.memory.aims.truth(), [])

    def test_temporary_context_and_queries_never_become_durable_atoms(self):
        first = self.memory.start("orb")
        self.memory.remember(first, {"user": "Private transient nebula", "assistant": "ok"})
        entries = self.memory.aims.long_term.total_entries
        self.memory.recall(first, "private transient nebula")
        self.memory.end(first)
        second = self.memory.start("orb")
        self.assertEqual(self.memory.recall(second, "nebula")["results"], [])
        self.assertEqual(self.memory.aims.long_term.total_entries, entries)
        self.assertEqual(self.memory.aims.retrieval_ledger.recent(), [])

    def test_temporal_edges_replay_and_reconciliation_is_idempotent(self):
        session = self.memory.start("orb")
        first = self.memory.remember(session, {"user": "Workshop blue"}, True, "Owner selected")
        second = self.memory.remember(session, {"user": "Workshop green", "recalled_atom_ids": [first["atom_id"]]}, True, "Owner selected")
        self.assertEqual(len(self.memory.aims.skg.all_edges()), 2)
        count = len(self.memory.aims.vault.all_atoms())
        self.memory.knowledge.reconcile()
        self.assertEqual(len(self.memory.aims.vault.all_atoms()), count)
        reloaded = HostMemory(Path(self.temp.name))
        try:
            self.assertEqual(len(reloaded.aims.skg.all_edges()), 2)
            self.assertEqual(reloaded.sessions, {})
            active = reloaded.start("orb")
            self.assertEqual(len(reloaded.recall(active, "workshop")["results"]), 2)
        finally:
            reloaded.db.close()

    def test_old_configuration_is_superseded_in_recall(self):
        first = self.memory.save_collection("dock.profiles", {"theme": "copper"}, "dock", "configuration")
        second = self.memory.save_collection("dock.profiles", {"theme": "silver"}, "dock", "configuration", first["entry_id"])
        session = self.memory.start("orb")
        records = self.memory.recall(session, "profiles theme")["results"]
        self.assertEqual([item["atom_id"] for item in records], [second["atom_id"]])
        self.assertEqual(self.memory.recall(session, "copper")["results"], [])

    def test_missing_promotion_after_persist_is_repaired_on_restart(self):
        session = self.memory.start("orb")
        with patch.object(self.memory.knowledge, "record", side_effect=OSError("index unavailable")):
            with self.assertRaises(OSError):
                self.memory.remember(session, {"user": "Important cobalt record"}, True, "Owner selected")
        reloaded = HostMemory(Path(self.temp.name))
        try:
            new = reloaded.start("orb")
            self.assertEqual(len(reloaded.recall(new, "cobalt")["results"]), 1)
        finally:
            reloaded.db.close()
