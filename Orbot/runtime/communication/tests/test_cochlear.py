import io
import unittest
from unittest.mock import Mock, patch
import numpy as np
import soundfile as sf
from runtime.communication.cochlear import CochlearInput
from runtime.communication.tests import test_service as service_tests
from runtime.communication import service


class HearingTests(unittest.TestCase):
    def wav(self, samples):
        stream = io.BytesIO()
        sf.write(stream, samples, 16000, format='WAV', subtype='PCM_16')
        return stream.getvalue()

    def test_silence_rejected_before_model_load(self):
        hearing = CochlearInput()
        with self.assertRaisesRegex(ValueError, 'audible'):
            hearing.transcribe(self.wav(np.zeros(16000)))
        self.assertIsNone(hearing.model)

    def test_real_stages_preserve_original_and_intentional_dropout(self):
        hearing = CochlearInput()
        hearing.model = Mock()
        hearing.model.transcribe.return_value = {'segments': [{'avg_logprob': -.01,
            'words': [{'word': 'hello'}, {'word': 'Orbot'}]}]}
        audio = np.sin(np.arange(16000)*.2)*.3
        trace = hearing.transcribe(self.wav(audio))
        self.assertEqual(trace['original_transcript'], 'hello Orbot')
        self.assertTrue(trace['perceptual']['dropouts'])
        self.assertFalse(trace['verified'])
        self.assertFalse(trace['execution_authority'])

    def test_dropout_hint_is_never_inserted_as_a_spoken_word(self):
        from cognitive_inference import CognitiveInferenceEngine
        engine = CognitiveInferenceEngine()
        with patch.object(engine, '_phonetic_neighbors', return_value=[]):
            word, sources = engine._infer_word('Orbot', 0, ['Orbot'], {'dropouts':[{}]})
        self.assertEqual(word, 'Orbot')
        self.assertEqual(sources['dropout_hint'], 'missing_phonemes')


class VoiceRouting(unittest.TestCase):
    setUp = service_tests.CommunicationTests.setUp
    tearDown = service_tests.CommunicationTests.tearDown
    def test_voice_uses_session_memory_and_requests_speech(self):
        session = self.client.post('/sessions', json={}).json()['session_id']
        trace = {'text': 'hello', 'original_transcript': 'hello', 'hearing_profile': {}}
        with patch.object(service.hearing, 'transcribe', return_value=trace), \
             patch.object(service.language, 'reply', return_value='Hello'), \
             patch.object(service.speech, 'synthesize', return_value=b'wav'):
            result = self.client.post('/voice/input', json={'session_id':session, 'audio_wav':'d2F2'})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(self.memory.items(session)[0]['hearing'], trace)
        self.assertFalse(result.json()['execution_authority'])

    def test_invalid_audio_does_not_reach_inference(self):
        session = self.client.post('/sessions', json={}).json()['session_id']
        with patch.object(service.language, 'reply') as reply:
            result = self.client.post('/voice/input', json={'session_id':session,'audio_wav':'!!!'})
        self.assertEqual(result.status_code,422)
        reply.assert_not_called()


    def test_inferred_corrections_cannot_replace_the_owners_recognized_speech(self):
        session = self.client.post('/sessions',json={}).json()['session_id']
        trace={'text':'invented correction','original_transcript':'actual spoken words','hearing_profile':{}}
        with patch.object(service.hearing,'transcribe',return_value=trace), patch.object(service.language,'reply',return_value='Hello') as reply, patch.object(service.speech,'synthesize',return_value=b'wav'):
            result=self.client.post('/voice/input',json={'session_id':session,'audio_wav':'d2F2'})
        self.assertEqual(result.status_code,200)
        self.assertEqual(reply.call_args.args[0],'actual spoken words')
        self.assertEqual(result.json()['hearing']['text'],'invented correction')
        self.assertEqual(self.memory.items(session)[0]['hearing'],trace)
