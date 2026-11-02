// Local energy-based turn boundaries. This is not a transcript, identity check,
// wake-word model or authorization decision.
export class VoiceActivity {
  active = false;
  speechMs = 0;
  silenceMs = 0;
  elapsedMs = 0;
  reset() { this.active = false; this.speechMs = 0; this.silenceMs = 0; this.elapsedMs = 0; }
  observe(samples: Float32Array, rate: number): 'waiting' | 'speech' | 'complete' {
    if (!samples.length || rate <= 0) return 'waiting';
    const duration = samples.length * 1000 / rate;
    const energy = Math.sqrt(samples.reduce((sum, value) => sum + value * value, 0) / samples.length);
    if (energy >= 0.012) {
      this.speechMs += duration;
      this.silenceMs = 0;
      if (this.speechMs >= 170) this.active = true;
    } else if (this.active) this.silenceMs += duration;
    else this.speechMs = 0;
    if (this.active) this.elapsedMs += duration;
    if (this.active && (this.silenceMs >= 800 || this.elapsedMs >= 15000)) return 'complete';
    return this.active ? 'speech' : 'waiting';
  }
}
