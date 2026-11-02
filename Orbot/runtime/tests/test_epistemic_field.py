import unittest
from fastapi.testclient import TestClient
from runtime.cognition_governance.service import app


class FieldIntegration(unittest.TestCase):
    def test_real_substrate_receives_observation_without_authority(self):
        client = TestClient(app)
        result = client.post('/field/observe', json={
            'recalled_count': 2, 'word_confidence': 0.6})
        self.assertEqual(result.status_code, 200)
        data = result.json()
        self.assertGreaterEqual(data['stats']['step_count'], 4)
        self.assertGreater(data['stats']['diffusion_energy'], 0)
        self.assertFalse(data['execution_authority'])
        self.assertFalse(data['verified'])
        self.assertEqual(client.post('/field/observe', json={
            'recalled_count': 0, 'word_confidence': 2}).status_code, 422)
