import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from runtime.communication import service
from runtime.communication.tests import test_service as service_tests
from runtime.communication.voice_turns import VoiceTurns, VoiceCancelled
import unittest


class CancellationRegistryTests(unittest.TestCase):
    def test_old_turn_cannot_cancel_new_turn_or_other_session(self):
        turns = VoiceTurns()
        first = turns.begin('session-a', 'old')
        turns.end(first)
        second = turns.begin('session-a', 'new')
        self.assertFalse(turns.cancel('session-a', 'old'))
        self.assertFalse(turns.cancel('session-b', 'new'))
        second.check()
        self.assertTrue(turns.cancel('session-a', 'new'))
        with self.assertRaises(VoiceCancelled):
            second.check()


class CancellationRouteTests(unittest.TestCase):
    setUp = service_tests.CommunicationTests.setUp
    tearDown = service_tests.CommunicationTests.tearDown

    def test_microphone_preferences_use_existing_authenticated_writer(self):
        value = {'device_id':'fixture-device','label':'Desktop Microphone'}
        with patch.object(service,'dock_token',return_value='fixture'):
            self.assertEqual(self.client.post('/voice/preferences',json=value).status_code,401)
            headers = {'Authorization':'Bearer fixture'}
            self.assertEqual(self.client.post('/voice/preferences',json=value,headers=headers).status_code,200)
            result = self.client.get('/voice/preferences',headers=headers)
            self.assertEqual(result.json()['value'],value)
            self.assertEqual(self.memory.collection('dock.voice_preferences'),value)
            self.assertEqual(self.client.get('/voice/last-turn').status_code,401)

    def test_cancel_during_recognition_suppresses_inference_and_preserves_session(self):
        session = self.memory.start_embodiment()
        started, release = threading.Event(), threading.Event()
        def transcribe(*args):
            started.set()
            self.assertTrue(release.wait(5))
            return {'text':'hello', 'hearing_profile':{}}
        with patch.object(service.hearing, 'transcribe', side_effect=transcribe), patch.object(service.language, 'reply') as reply, patch.object(service, 'dock_token', return_value='fixture'):
            with ThreadPoolExecutor(1) as pool:
                pending = pool.submit(self.client.post, '/voice/input', json={'session_id':session,'turn_id':'fixture-turn','audio_wav':'d2F2'})
                self.assertTrue(started.wait(5))
                self.assertEqual(self.client.post('/voice/cancel',json={}).status_code,401)
                result = self.client.post('/voice/cancel',json={'turn_id':'fixture-turn'},headers={'Authorization':'Bearer fixture'})
                release.set()
                self.assertEqual(pending.result(timeout=5).status_code,409)
        self.assertTrue(result.json()['cancel_requested'])
        self.assertEqual(self.memory.start_embodiment(),session)
        self.assertEqual(self.memory.items(session),[])
        reply.assert_not_called()

    def test_cancelled_synthesis_cannot_release_audio_or_remember_assistant_reply(self):
        session = self.memory.start_embodiment()
        trace = {'text':'hello', 'hearing_profile':{}}
        def synthesize(text, cancelled):
            cancelled.set()
            return b'stale audio'
        with patch.object(service.hearing,'transcribe',return_value=trace), patch.object(service.language,'reply',return_value='Hello'), patch.object(service.speech,'synthesize',side_effect=synthesize):
            result = self.client.post('/voice/input',json={'session_id':session,'audio_wav':'d2F2'})
        self.assertEqual(result.status_code,409)
        self.assertEqual(len(self.memory.items(session)),1)
        self.assertNotIn('assistant',self.memory.items(session)[0])
