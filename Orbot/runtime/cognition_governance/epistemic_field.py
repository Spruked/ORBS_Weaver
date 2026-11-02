"""Session-independent, volatile advisory substrate; never a truth/permit issuer."""
from threading import Lock
import importlib.util
from pathlib import Path
import sys

import torch

# Load the supplied substrate without executing TPC's unrelated legacy initializer.
_path = Path(__file__).resolve().parents[2] / "Triple_Predicate_Cubed/Epistemic_Gravity_Field/space_field.py"
_spec = importlib.util.spec_from_file_location("orbot_space_field", _path)
_module = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _module
_spec.loader.exec_module(_module)
SpaceFieldCognition = _module.SpaceFieldCognition


class EpistemicField:
    def __init__(self):
        self._field = None
        self._lock = Lock()

    def initialize(self):
        """Allocate the existing advisory substrate, without inventing evidence."""
        with self._lock, torch.inference_mode():
            if self._field is None:
                self._field = SpaceFieldCognition(device="cpu")
            return self._snapshot()

    def observe(self, recalled_count: int, word_confidence: float):
        # These are input characteristics, not evidence that a claim is true.
        with self._lock, torch.inference_mode():
            if self._field is None:
                self._field = SpaceFieldCognition(device="cpu")
            field = self._field
            signal = torch.zeros_like(field.diffusion.field)
            outer = field.cubes.shell_mask["outer"].view(32, 32, 32)
            signal[outer] = torch.tensor([
                1.0, min(recalled_count, 10) / 10.0, word_confidence,
                1.0 - word_confidence,
            ])
            field.broadcast_to_field(signal)
            # Four ticks exercise each shell's existing cadence.
            for _ in range(4):
                field.step()
            return self._snapshot()

    def snapshot(self):
        with self._lock:
            return self._snapshot()

    def _snapshot(self):
        return {"available": True, "initialized": self._field is not None,
                "stats": self._field.get_field_stats() if self._field else {},
                "advisory_only": True, "verified": False,
                "execution_authority": False}
