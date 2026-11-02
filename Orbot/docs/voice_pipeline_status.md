> GPU deployment update: Qwen3-TTS now executes on CUDA with bounded CPU weight offloading, with no automatic CPU inference fallback. Earlier CPU measurements below are historical. See [qwen_gpu_integration_report.md](qwen_gpu_integration_report.md).

# Local voice pipeline

Required deployment: local Whisper/cochlear hearing → Qwen2.5-7B-Instruct through shared llama.cpp on 16520 → Qwen3-TTS output. Browser/Windows speech engines are not used. WebView provides device capture, energy-based utterance boundaries and WAV playback only.

## Current lifecycle requirement

Voice is first, starts automatically, and remains available while docked. Docking changes presentation only. Explicit Pause voice, Cancel reply and application shutdown suspend/cancel media. Click interaction is a manual fallback/control.

The selected input is Desktop Microphone (Realtek(R) Audio), explicitly confirmed and renamed by the owner. Its exact device ID and label are persisted through the existing HostMemory/AIMS writer as dock.voice_preferences. Missing selected inputs produce an actionable error; they do not silently fall back. Dock includes microphone enumeration and selection.

Capture is continuous across turns; it does not close/reopen the device after every rejected utterance. Pending requests have correlated cancellation and stale output suppression. Qwen cancellation checks run between generation forward steps; current STT/inference calls and model load/decode may finish before a cancellation check.

Optional retrieved evidence is budgeted with actual llama.cpp token measurements. Omitted AIMS atom IDs are explicit. Full inculcation and retained conversation history are never shortened; a conversation that exceeds capacity still fails closed. Per-turn overflow no longer changes lifecycle readiness or causes coordinator shutdown.

The raw Whisper transcript is the conversation input. Cochlear inferred corrections remain separately labeled unverified observations. Conversation remains non-executing; full TPC/RAL/Doctrine enforcement is still not integrated.

See voice_runtime_integration_report.md for measured results and limitations.
