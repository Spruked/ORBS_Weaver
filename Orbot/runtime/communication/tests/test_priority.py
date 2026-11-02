import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runtime.communication.memory import HostMemory


class PriorityCacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.memory = HostMemory(Path(self.temp.name))
        self.session = self.memory.start("orb")

    def tearDown(self):
        self.memory.db.close()
        self.temp.cleanup()

    def remember(self, text, priority, refs=None):
        return self.memory.remember(self.session, {"user": text, "recalled_atom_ids": refs or []},
            priority=priority, reason="Owner priority" if priority == "high" else "")

    def test_three_caches_and_high_survives_purge(self):
        high = self.remember("High priority project", "high")
        self.remember("Ordinary note", "medium")
        self.remember("Temporary note", "low")
        counts = self.memory.cache_status(self.session)
        self.assertEqual([counts[key]["count"] for key in ("high", "medium", "low")], [1, 1, 1])
        report = self.memory.end(self.session)
        self.assertEqual(report["retained_high"], 1)
        self.assertEqual(report["pruned"], 2)
        other = self.memory.start("new")
        self.assertEqual(self.memory.recall(other, "project")["results"][0]["priority"], "high")
        self.assertIsNotNone(high["atom_id"])

    def test_skg_linked_medium_is_saved_at_close(self):
        high = self.remember("Important workshop", "high")
        medium = self.remember("Useful related workshop", "medium", [high["atom_id"]])
        self.assertFalse(medium["retained"])
        report = self.memory.end(self.session)
        self.assertEqual(report["saved"], 1)
        fresh = self.memory.start("new")
        result = self.memory.recall(fresh, "useful")["results"][0]
        self.assertEqual(result["priority"], "medium")
        self.assertFalse(result["verified"])

    def test_low_requires_both_repetition_and_graph_relevance(self):
        high = self.remember("Important workshop", "high")
        for _ in range(3):
            self.remember("Recurring related note", "low", [high["atom_id"]])
        self.remember("Single related note", "low", [high["atom_id"]])
        report = self.memory.end(self.session)
        self.assertEqual(report["saved"], 1)
        self.assertEqual(report["duplicates"], 2)
        self.assertEqual(report["pruned"], 1)

    def test_failed_close_preserves_cache_and_retry_does_not_duplicate(self):
        high = self.remember("Important anchor", "high")
        self.remember("Unrelated review candidate", "medium")
        self.remember("Related pending record", "medium", [high["atom_id"]])
        with patch.object(self.memory.knowledge, "record", side_effect=OSError("graph unavailable")):
            with self.assertRaises(OSError):
                self.memory.end(self.session)
        self.assertIn(self.session, self.memory.sessions)
        with self.assertRaises(ValueError):
            self.remember("Cannot append during failed closing", "low")
        entries = self.memory.aims.long_term.total_entries
        report = self.memory.end(self.session)
        self.assertEqual(report["saved"], 1)
        self.assertEqual(report["pruned"], 1)
        self.assertEqual(self.memory.aims.long_term.total_entries, entries)

    def test_expiry_runs_review_before_clearing(self):
        high = self.remember("Important anchor", "high")
        self.remember("Pending related information", "medium", [high["atom_id"]])
        self.memory.sessions[self.session]["last"] -= 1900
        self.memory.expire()
        self.assertNotIn(self.session, self.memory.sessions)
        fresh = self.memory.start("new")
        self.assertEqual(self.memory.recall(fresh, "pending")["results"][0]["priority"], "medium")

    def test_repeated_high_does_not_duplicate_durable_records(self):
        first = self.remember("Important repeated note", "high")
        second = self.remember("Important repeated note", "high")
        self.assertEqual(first["entry_id"], second["entry_id"])

    def test_capacity_eviction_runs_review_and_saved_record_is_not_duplicated(self):
        high = self.remember("Important capacity anchor", "high")
        self.memory.sessions[self.session]["caches"]["low"].capacity = 1
        for _ in range(3):
            self.remember("Recurring linked capacity note", "low", [high["atom_id"]])
        report = self.memory.end(self.session)
        self.assertEqual(report["saved"], 1)
        next_session = self.memory.start("new")
        result = self.memory.recall(next_session, "recurring")["results"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["priority"], "medium")
