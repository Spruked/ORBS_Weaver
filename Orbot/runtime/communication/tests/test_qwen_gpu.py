import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
import torch
from runtime.communication.providers import QwenSpeechProvider
from runtime.communication.qwen_gpu import gpu_plan, residency_map, QwenGpuCapacityError


class QwenGpuTests(unittest.TestCase):
    def test_shared_gpu_uses_a_bounded_allocator(self):
        plan = gpu_plan(1200*1024**2, 8*1024**3)
        self.assertEqual(plan['mode'], 'cuda_weight_offload')
        self.assertEqual(plan['allocator_budget_mib'],768)
        self.assertLess(plan['allocator_fraction'],.1)

    def test_insufficient_headroom_fails_instead_of_falling_back(self):
        with self.assertRaises(QwenGpuCapacityError):
            gpu_plan(900*1024**2,8*1024**3)

    def test_unshared_gpu_can_use_full_cuda_residency(self):
        self.assertEqual(gpu_plan(7*1024**3,8*1024**3)['mode'],'cuda')

    def test_direct_codec_decode_subtree_is_not_offloaded_to_meta(self):
        model = torch.nn.Module()
        model.decoder = torch.nn.Module()
        model.decoder.quantizer = torch.nn.Sequential(torch.nn.Linear(2,2))
        model.decoder.other = torch.nn.Linear(2,2)
        mapping = residency_map(model,resident_subtrees=('decoder.quantizer',))
        self.assertEqual(mapping['decoder.quantizer'],'cuda:0')
        self.assertNotIn('decoder.quantizer.0',mapping)
        self.assertEqual(mapping['decoder.other'],'cpu')

    def test_auto_requires_cuda_before_loading_any_weights(self):
        provider=QwenSpeechProvider()
        provider.device='auto'
        model_type=SimpleNamespace(from_pretrained=Mock())
        with patch.dict(sys.modules,{'qwen_tts':SimpleNamespace(Qwen3TTSModel=model_type)}), patch.object(torch.cuda,'is_available',return_value=False):
            with self.assertRaises(QwenGpuCapacityError):
                provider.synthesize('Hello')
        model_type.from_pretrained.assert_not_called()
