import unittest
from runtime.shared.diagnostics import RuntimeDiagnostics, metric
from fastapi.testclient import TestClient
from runtime.motion.service import app


class DiagnosticsTests(unittest.TestCase):
    def test_unknown_is_distinct_from_measured_false_and_zero(self):
        self.assertEqual(metric()["status"], "unknown")
        self.assertIsNone(metric()["measured_at"])
        for value in (False, 0):
            self.assertEqual(metric(value)["status"], "measured")
            self.assertIsNotNone(metric(value)["measured_at"])

    def test_instances_and_readiness_are_not_invented(self):
        first, second = RuntimeDiagnostics("test"), RuntimeDiagnostics("test")
        self.assertNotEqual(first.instance, second.instance)
        snapshot = first.snapshot()
        self.assertTrue(snapshot["metrics"]["running"]["value"])
        self.assertIsNone(snapshot["metrics"]["policy_validated"]["value"])

    def test_motion_disabled_does_not_claim_watchdog_armed(self):
        result = TestClient(app).get('/diagnostics').json()
        self.assertFalse(result['metrics']['enabled']['value'])
        self.assertNotIn('watchdog', result['metrics'])
