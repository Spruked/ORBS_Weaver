# Orb cochlear input

The undocked Orb has no chat view. Click once to open the microphone, click
again to submit, or let its 20-second capture limit submit the utterance.
Click during speech playback to stop it. Microphone capture stops before the
reply plays. Right-click still opens docking controls. Text chat belongs in the
external Dock Station beside its docking bay; relocating the former chat UI
there remains separate work.

Communication `/voice/input` accepts a live AIMS session and bounded PCM16 WAV.
It validates format, duration, and audible input, downmixes/resamples to 16 kHz,
then runs the existing TPC V3 SKG perceptual filter, including intentional
random dropouts and attention effects, local Whisper recognition, cognitive
inference, correction monitoring, and the SKG correction-learning bridge.
Recognition uses Whisper base on CPU to leave GPU capacity for llama.cpp and
Qwen3-TTS **1.7B**. Whisper is local software; no speech API is used.

The adapter preserves original ASR text, word confidence estimates, guessed
corrections, noticed corrections, dropout metadata, and the session hearing
profile in AIMS Low-priority working memory. Subsequent utterances reload that
profile from the same session. Existing close-review rules govern retention.
Raw microphone recordings are not written to a private file. The V3 private
trace writer and JSON graph writer are bypassed; AIMS remains the memory owner.
An inferred hearing correction is not verified speaker intent or authority.

Review findings addressed:

- Legacy inference emits `inferred`; learning expects `corrected` and `phoneme`.
  The adapter maps these fields and labels learned corrections as inferred.
  Word tokens serve as provisional learning keys, not measured phonetic labels.
- `missing_phonemes` was incorrectly eligible to become a spoken word. It now
  remains metadata while intentional dropout behavior is preserved.
- Legacy learning prints emoji that fail under Windows cp1252. Adapter calls
  capture those diagnostic prints without exposing utterances to console logs.
- `FastCochlearProcessor` references an unset `asr_cpp` and passes arrays to a
  path-taking API; it is not used for this integration.
- AdaptivePlasticity's cross-utterance experience log and automatic voice
  re-synthesis callbacks are not connected in this slice. Inference and
  correction probabilities remain the component's heuristic prototype logic.

Validation: Communication suite (32 tests) and desktop frontend build pass.
Actual local Whisper recognition through the TPC stages was exercised on the
existing recorded speech fixture. Physical microphone capture/permissions and
speaker playback in WebView2 still require an interactive desktop check.
Restart/rebuild the native application and Communication service to load these
changes; source changes alone do not update already-running processes.
