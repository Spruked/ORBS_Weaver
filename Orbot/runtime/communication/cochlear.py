"""TPC hearing adaptation. Interpretations are observations, never authority."""
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
from math import gcd
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'Triple_Predicate_Cubed/cochlear_processor_3.0'
# The imported legacy component uses sibling imports and has a dotted directory.
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))
from cochlear_processor_v3 import CochlearProcessorV3
from skg_perceptual_filter import SpeakerKnowledgeGraph, SKGPerceptualFilter


class SessionGraph(SpeakerKnowledgeGraph):
    def __init__(self, data=None):
        # Ask the component for its neutral default, without a private file.
        self.skg_path = str(SOURCE / '__unused_session_profile__')
        self.data = data if data is not None else self._load_skg()

    def _save_skg(self):
        pass  # Session profile is returned to AIMS instead of written privately.


class CochlearInput:
    def __init__(self):
        self.model = None

    def transcribe(self, wav, profile=None):
        with sf.SoundFile(io.BytesIO(wav)) as stream:
            if stream.format != 'WAV' or stream.subtype != 'PCM_16':
                raise ValueError('16-bit PCM WAV required')
            if not 8000 <= stream.samplerate <= 96000 or stream.channels not in (1, 2):
                raise ValueError('Unsupported audio format')
            if not 0.25 <= stream.frames / stream.samplerate <= 30:
                raise ValueError('Audio must be between 0.25 and 30 seconds')
            rate = stream.samplerate
            audio = stream.read(dtype='float32', always_2d=True).mean(axis=1)
        if not np.isfinite(audio).all() or np.max(np.abs(audio)) < 0.001:
            raise ValueError('No audible input')
        divisor = gcd(rate, 16000)
        audio = resample_poly(audio, 16000 // divisor, rate // divisor).astype(np.float32)
        # Build the real V3 stages without its file-based constructor/writer.
        from cognitive_inference import CognitiveInferenceEngine
        from correction_loop import RealtimeCorrectionLoop
        from skg_learning_bridge import SKGLearningBridge
        processor = CochlearProcessorV3.__new__(CochlearProcessorV3)
        processor.skg = SessionGraph(profile)
        processor.perceptual_filter = SKGPerceptualFilter(processor.skg)
        processor.cognitive_engine = CognitiveInferenceEngine()
        processor.correction_loop = RealtimeCorrectionLoop(processor)
        processor.learning_bridge = SKGLearningBridge(processor.skg, processor.perceptual_filter)
        filtered, report = processor.perceptual_filter.apply_perceptual_filter(audio, {})
        if self.model is None:
            import whisper
            self.model = whisper.load_model('base', device='cpu', download_root=str(ROOT / '.local/models/whisper'))
        processor._whisper_model = self.model
        original, confidences = processor._transcribe_with_confidence(filtered.astype(np.float32), 16000)
        if not original.strip() or len(original) > 2000:
            raise ValueError('Speech was unclear; please repeat')
        inferred, corrections = processor.cognitive_engine.process_with_inference(original, confidences, report)
        noticed = []
        final = processor.correction_loop.monitor_and_correct(inferred,
            on_correction=lambda wrong, right: noticed.append({'original': wrong, 'inferred': right}),
            word_confidences=confidences)
        # The legacy learning bridge expects corrected/phoneme, but inference
        # supplies inferred/position. Preserve that distinction explicitly.
        for correction in corrections:
            with redirect_stdout(io.StringIO()):
                processor.learning_bridge.process_correction({**correction,
                    'corrected': correction['inferred'], 'phoneme': correction['original'].lower(),
                    'speaker': 'unidentified', 'context': 'orb-session', 'inferred_only': True})
        trace = {'text': final, 'original_transcript': original, 'word_confidences': confidences,
            'corrections': corrections, 'noticed_corrections': noticed, 'perceptual': report,
            'hearing_profile': processor.skg.data, 'processor': 'tpc_cochlear_v3',
            'verified': False, 'execution_authority': False}
        return json.loads(json.dumps(trace, default=lambda value: value.item()))
