import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from runtime.communication import service


class CommunicationTests(unittest.TestCase):
    def setUp(self):
        from runtime.communication.memory import HostMemory
        self.temp = tempfile.TemporaryDirectory()
        self.memory = HostMemory(Path(self.temp.name))
        self.memory_patch = patch.object(service, "get_memory", return_value=self.memory)
        self.memory_patch.start()
        self.client = TestClient(service.app)

    def tearDown(self):
        self.memory_patch.stop()
        self.memory.db.close()
        self.temp.cleanup()

    def test_untrusted_web_origin_is_rejected(self):
        result = self.client.post("/conversation", json={"text": "hello"},
                                  headers={"Origin": "https://example.com"})
        self.assertEqual(result.status_code, 403)

    def test_action_fields_cannot_enter_conversation(self):
        result = self.client.post("/conversation", json={"text": "hello", "execute": True})
        self.assertEqual(result.status_code, 422)

    def test_blank_input_is_rejected(self):
        self.assertEqual(self.client.post("/conversation", json={"text": "  "}).status_code, 422)

    def test_speech_failure_preserves_text_without_granting_authority(self):
        with patch.object(service.language, "reply", return_value="Hello"), \
             patch.object(service.speech, "synthesize", side_effect=RuntimeError("offline")):
            result = self.client.post("/conversation", json={"text": "hello", "speak": True})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["text"], "Hello")
        self.assertIsNone(result.json()["audio_wav"])
        self.assertFalse(result.json()["execution_authority"])

    def test_model_failure_is_explicit(self):
        with patch.object(service.language, "reply", side_effect=RuntimeError("offline")):
            self.assertEqual(self.client.post("/conversation", json={"text": "hi"}).status_code, 503)

    def test_orb_reply_receives_vault_backed_recall_in_a_new_session(self):
        with patch.object(service.language, "reply", return_value="Recorded"):
            first = self.client.post("/conversation", json={"text": "Workshop project Blue Lantern", "important": True}).json()
        self.client.post("/sessions/end", json={"session_id": first["session_id"]})
        with patch.object(service.language, "reply", return_value="Blue Lantern") as provider:
            result = self.client.post("/conversation", json={"text": "What was the workshop project?"})
        self.assertEqual(result.status_code, 200)
        context = provider.call_args.args[2]
        self.assertEqual(context[0]["atom_id"], first["memory"]["atom_id"])
        self.assertEqual(result.json()["recall"]["results"][0]["source_entry_ids"], [first["memory"]["entry_id"]])

    def test_recall_requires_a_live_session(self):
        result = self.client.post("/memory/recall", json={"session_id": "closed", "query": "workshop"})
        self.assertEqual(result.status_code, 409)

    def test_priority_caches_and_closing_report_are_exposed_to_orb(self):
        with patch.object(service.language, "reply", return_value="Noted"):
            first = self.client.post("/conversation", json={"text": "High-priority anchor", "priority": "high"}).json()
            self.client.post("/conversation", json={"text": "Transient scratch note", "priority": "low", "session_id": first["session_id"]})
        caches = self.client.get(f'/sessions/{first["session_id"]}/caches').json()
        self.assertEqual(caches["high"]["count"], 1)
        self.assertEqual(caches["low"]["count"], 1)
        closed = self.client.post("/sessions/end", json={"session_id": first["session_id"]}).json()
        self.assertEqual(closed["close_review"]["pruned"], 1)
        self.assertEqual(closed["close_review"]["retained_high"], 1)


if __name__ == "__main__":
    unittest.main()
