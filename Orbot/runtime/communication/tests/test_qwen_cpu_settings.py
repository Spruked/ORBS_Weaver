import os
import unittest
from unittest.mock import patch
from runtime.communication.providers import QwenSpeechProvider


class QwenCpuSettingsTests(unittest.TestCase):
    def test_measured_cpu_defaults_do_not_change_model_or_voice(self):
        with patch.dict(os.environ, {'ORBOT_TTS_CPU_DTYPE':'float32','ORBOT_TTS_CPU_THREADS':'2'}):
            provider = QwenSpeechProvider()
        self.assertEqual(provider.cpu_precision, 'float32')
        self.assertEqual(provider.cpu_threads, 2)
        self.assertIn('Qwen3-TTS', provider.model_id)
        self.assertEqual(provider.speaker, 'Ryan')
        self.assertFalse(provider.loaded)
        self.assertIsNone(provider.active_precision)

    def test_explicit_bfloat16_rollback_is_available(self):
        with patch.dict(os.environ, {'ORBOT_TTS_CPU_DTYPE':'bfloat16'}):
            self.assertEqual(QwenSpeechProvider().cpu_precision, 'bfloat16')

    def test_invalid_settings_fail_before_loading_a_model(self):
        for values in ({'ORBOT_TTS_CPU_DTYPE':'int8'}, {'ORBOT_TTS_CPU_THREADS':'0'}):
            with patch.dict(os.environ, values):
                with self.assertRaises(ValueError):
                    QwenSpeechProvider()
