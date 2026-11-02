import tempfile
import unittest
from pathlib import Path

from runtime.communication.memory import HostMemory


class SessionMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.memory = HostMemory(Path(self.temp.name))
        self.initial_entries = self.memory.aims.long_term.total_entries

    def tearDown(self):
        self.memory.db.close()
        self.temp.cleanup()

    def test_sessions_are_isolated_and_end_discards_working_memory(self):
        first, second = self.memory.start("one"), self.memory.start("two")
        self.memory.remember(first, {"text": "private working context"})
        self.assertEqual(self.memory.items(second), [])
        self.memory.end(first)
        with self.assertRaises(ValueError):
            self.memory.items(first)
        self.assertEqual(self.memory.aims.long_term.total_entries, self.initial_entries)

    def test_important_records_survive_session_end_and_restart(self):
        session = self.memory.start("dock")
        result = self.memory.remember(session, {"text": "retained"}, True, "Owner selected")
        self.memory.end(session)
        reloaded = HostMemory(Path(self.temp.name))
        try:
            self.assertEqual(reloaded.sessions, {})
            entry = next(item for item in reloaded.aims.long_term.entries if item.entry_id == result["entry_id"])
            self.assertEqual(entry.metadata["retention_reason"], "Owner selected")
        finally:
            reloaded.db.close()

    def test_sqlite_is_rebuilt_and_conflicting_updates_rejected(self):
        result = self.memory.save_collection("dock.profiles", {"a": 1}, "dock", "configuration")
        with self.assertRaises(ValueError):
            self.memory.save_collection("dock.profiles", {"a": 2}, "dock", "configuration")
        self.memory.db.execute("DELETE FROM collections")
        self.memory.db.commit()
        self.memory.rebuild()
        self.assertEqual(self.memory.collection("dock.profiles"), {"a": 1})
        self.assertEqual(self.memory.collection_revision("dock.profiles"), result["entry_id"])

    def test_expired_working_memory_is_not_restored(self):
        session = self.memory.start("dock")
        self.memory.sessions[session]["last"] -= 1900
        with self.assertRaises(ValueError):
            self.memory.items(session)

    def test_important_requires_retention_reason(self):
        session = self.memory.start("dock")
        with self.assertRaises(ValueError):
            self.memory.remember(session, {"data": 1}, True)
