from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from runtime.communication.memory import HostMemory
from runtime.communication import service


class DockingSessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.memory = HostMemory(Path(self.temp.name), idle_seconds=1)

    def tearDown(self):
        self.memory.close_all()
        self.memory.db.close()
        self.memory.aims.close()
        self.temp.cleanup()

    def test_active_session_survives_docked_idle(self):
        session = self.memory.start_embodiment()
        self.memory.set_objective(session, "Continue project")
        self.memory.sessions[session]["last"] -= 3600
        self.memory.expire()
        self.assertEqual(self.memory.start_embodiment(), session)
        self.assertEqual(self.memory.working_context(session)["objective"], "Continue project")

    def test_ordinary_session_still_expires(self):
        active = self.memory.start_embodiment()
        ordinary = self.memory.start("ordinary")
        self.memory.sessions[ordinary]["last"] -= 3600
        self.memory.expire()
        self.assertIn(active, self.memory.sessions)
        self.assertNotIn(ordinary, self.memory.sessions)

    def test_explicit_end_reconciles_and_creates_clean_next_session(self):
        first = self.memory.start_embodiment()
        self.memory.remember(first, {"user": "Temporary continuity"})
        self.assertEqual(self.memory.end(first)["pruned"], 1)
        second = self.memory.start_embodiment()
        self.assertNotEqual(first, second)
        self.assertEqual(self.memory.items(second), [])

    def test_native_session_uses_existing_dock_authentication(self):
        with patch.object(service, "get_memory", return_value=self.memory), patch.object(service, "dock_token", return_value="fixture-only"):
            client = TestClient(service.app)
            self.assertEqual(client.post("/sessions/embodiment", json={}).status_code, 401)
            headers = {"Authorization": "Bearer fixture-only"}
            first = client.post("/sessions/embodiment", json={}, headers=headers).json()
            self.assertEqual(client.post("/sessions/embodiment", json={}, headers=headers).json(), first)
            self.assertEqual(client.get("/sessions/embodiment", headers=headers).json(), first)

    def test_shutdown_rejects_wrong_instance_without_session_loss(self):
        session = self.memory.start_embodiment()
        with patch.object(service, "get_memory", return_value=self.memory), patch.object(service, "dock_token", return_value="fixture-only"):
            result = TestClient(service.app).post("/lifecycle/shutdown", json={"process_instance_id": "wrong"},
                headers={"Authorization": "Bearer fixture-only"})
        self.assertEqual(result.status_code, 409)
        self.assertIn(session, self.memory.sessions)


if __name__ == "__main__":
    unittest.main()
