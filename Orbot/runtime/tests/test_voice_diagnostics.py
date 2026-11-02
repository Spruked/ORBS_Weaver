import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from runtime.communication import service
from runtime.communication.voice_diagnostics import VoiceDiagnostics
from runtime.cognition_governance.epistemic_field import EpistemicField


class VoiceMeasurementTests(unittest.TestCase):
    def test_turn_capacity_error_does_not_shut_down_healthy_runtime(self):
        foundation = service.loader.load()
        with patch.object(service, 'foundation_preflight', {'fits':True,'foundation_sha256':foundation.sha256}), patch.object(service.language,'context_status',{'fits':False},create=True):
            result = TestClient(service.app).get('/health')
        self.assertTrue(result.json()['ready'])

    def test_events_require_existing_dock_credential(self):
        with patch.object(service, 'dock_token', return_value='fixture'):
            client = TestClient(service.app)
            self.assertEqual(client.post('/voice/events', json={'state':'listening'}).status_code,401)
            result=client.post('/voice/events',json={'state':'listening','microphone':True},headers={'Authorization':'Bearer fixture'})
            self.assertEqual(result.status_code,200)
            self.assertEqual(result.json()['verification'],'client_report_not_hardware_audit')

    def test_telemetry_cannot_become_a_recording_or_transcript_sink(self):
        with patch.object(service, 'dock_token', return_value='fixture'):
            result=TestClient(service.app).post('/voice/events',json={'state':'listening','transcript':'private text'},headers={'Authorization':'Bearer fixture'})
            self.assertEqual(result.status_code,422)

    def test_synthesized_audio_is_not_verified_playback(self):
        with patch.object(service, 'dock_token', return_value='fixture'), patch.object(service.speech,'synthesize',return_value=b'fixture'):
            result=TestClient(service.app).post('/voice/synthesize',json={'text':'Hello'},headers={'Authorization':'Bearer fixture'})
        self.assertEqual(result.status_code,200)
        self.assertFalse(result.json()['playback_verified'])

    def test_substrate_allocation_does_not_fabricate_observations(self):
        field=EpistemicField()
        first=field.initialize(); underlying=field._field
        second=field.initialize()
        self.assertTrue(first['initialized'])
        self.assertIs(field._field,underlying)
        self.assertEqual(second['stats']['step_count'],0)
        self.assertFalse(second['verified'])
        self.assertFalse(second['execution_authority'])


if __name__=='__main__': unittest.main()
