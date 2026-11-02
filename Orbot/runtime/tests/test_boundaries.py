import unittest
from fastapi.testclient import TestClient
from runtime.motion.service import app as motion
from runtime.cognition_governance.service import app as cognition
from runtime.shared.health import PORTS


class RuntimeBoundaries(unittest.TestCase):
    def test_three_distinct_ports(self):
        self.assertEqual(len(PORTS), 3)
        self.assertEqual(len(set(PORTS.values())), 3)

    def test_motion_rejects_even_claimed_permit(self):
        client = TestClient(motion)
        self.assertFalse(client.get('/health').json()['execution_authority'])
        self.assertEqual(client.post('/commands', json={'permit_id': 'invented'}).status_code, 503)

    def test_cognition_does_not_expose_a_permit_issuer(self):
        client = TestClient(cognition)
        health = client.get('/health').json()
        self.assertEqual(len(health['core4']), 4)
        self.assertFalse(health['permit_authority_ready'])
        self.assertEqual(client.post('/permits', json={'authority': 'action'}).status_code, 404)
