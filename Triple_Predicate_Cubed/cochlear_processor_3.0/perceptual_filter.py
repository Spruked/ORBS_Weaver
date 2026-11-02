import numpy as np
from scipy.signal import butter, lfilter
from dataclasses import dataclass
from typing import Tuple, Dict, Optional

@dataclass
class PerceptualState:
    attention_level: float = 0.8          # 0.0-1.0 (fatigued to hyper-focused)
    frequency_sensitivity: Dict[float, float] = None  # Hz: sensitivity
    recent_phoneme_memory: list = None    # Last 10 phonemes for context
    confidence_decay: float = 0.95        # Temporal decay factor
    
class HumanPerceptualFilter:
    """
    Simulates biological hearing limitations and attention effects.
    """
    
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.state = PerceptualState()
        self._init_frequency_sensitivity()
        
    def _init_frequency_sensitivity(self):
        """Human ear is most sensitive at 2-5 kHz; less at extremes"""
        self.state.frequency_sensitivity = {
            # Normal human hearing range: 20Hz-20kHz
            # Sensitivity modeled as inverted U-curve
            20: 0.10, 100: 0.30, 500: 0.60, 2000: 1.0,  # Peak sensitivity
            5000: 1.0, 10000: 0.70, 15000: 0.40, 20000: 0.15
        }
    
    def apply_perceptual_filter(self, audio_chunk: np.ndarray, 
                              attention_override: float = None) -> Tuple[np.ndarray, Dict]:
        """
        Physiologically-accurate hearing simulation.
        Returns filtered audio + perceptual metadata.
        """
        if attention_override is not None:
            self.state.attention_level = attention_override
        
        # 1. Frequency masking (less sensitive to extremes when fatigued)
        filtered_audio = self._frequency_masking(audio_chunk)
        
        # 2. Attention gating (reduces amplitude when distracted)
        filtered_audio = self._attention_gate(filtered_audio)
        
        # 3. Temporal smearing (blurs rapid transients)
        filtered_audio = self._temporal_smearing(filtered_audio)
        
        # 4. Simulated hearing loss (random dropouts)
        filtered_audio, dropout_report = self._simulated_dropout(filtered_audio)
        
        perceptual_report = {
            "attention_level": self.state.attention_level,
            "dropouts": dropout_report,
            "frequency_band_attenuation": self._calculate_attenuation(),
            "confidence_factor": self._calculate_confidence()
        }
        
        return filtered_audio, perceptual_report
    
    def _frequency_masking(self, audio: np.ndarray) -> np.ndarray:
        """Apply human frequency sensitivity curve"""
        # FFT to frequency domain
        fft = np.fft.rfft(audio)
        freqs = np.fft.rfftfreq(len(audio), 1/self.sample_rate)
        
        # Apply sensitivity curve
        for i, freq in enumerate(freqs):
            sensitivity = self._interpolate_sensitivity(freq)
            fft[i] *= sensitivity * self.state.attention_level
        
        # IFFT back to time domain
        return np.fft.irfft(fft)
    
    def _attention_gate(self, audio: np.ndarray) -> np.ndarray:
        """Attention acts as amplitude gate (0.7 = 30% reduction)"""
        gate_factor = 0.7 + (self.state.attention_level * 0.3)
        return audio * gate_factor
    
    def _temporal_smearing(self, audio: np.ndarray) -> np.ndarray:
        """Blurs rapid transients (simulates auditory nerve processing lag)"""
        if self.state.attention_level < 0.5:
            # Apply gentle low-pass filter when fatigued
            b, a = butter(2, 0.5)  # 0.5 * Nyquist frequency
            return lfilter(b, a, audio)
        return audio
    
    def _simulated_dropout(self, audio: np.ndarray, dropout_rate: float = 0.02) -> Tuple[np.ndarray, list]:
        """Simulates mishearing: random 20ms dropouts"""
        dropout_duration = int(0.02 * self.sample_rate)  # 20ms
        n_dropouts = int(len(audio) * dropout_rate / dropout_duration)
        
        dropouts = []
        for _ in range(n_dropouts):
            start = np.random.randint(0, len(audio) - dropout_duration)
            audio[start:start+dropout_duration] = 0
            dropouts.append({"start_ms": start * 1000 / self.sample_rate, "duration_ms": 20})
        
        return audio, dropouts
    
    def _calculate_confidence(self) -> float:
        """Confidence decays with attention fatigue and dropouts"""
        return self.state.attention_level * self.state.confidence_decay
    
    def _calculate_attenuation(self) -> Dict:
        """Calculate frequency band attenuation applied"""
        return {f"{freq}Hz": 1.0 - sens for freq, sens in self.state.frequency_sensitivity.items()}
    
    def _interpolate_sensitivity(self, freq: float) -> float:
        """Linear interpolation of frequency sensitivity curve"""
        freqs = sorted(self.state.frequency_sensitivity.keys())
        for i in range(len(freqs) - 1):
            if freqs[i] <= freq <= freqs[i+1]:
                low, high = freqs[i], freqs[i+1]
                sens_low = self.state.frequency_sensitivity[low]
                sens_high = self.state.frequency_sensitivity[high]
                return sens_low + (sens_high - sens_low) * ((freq - low) / (high - low))
        return 0.1  # Default for out-of-range