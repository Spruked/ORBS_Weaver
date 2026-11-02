> GPU deployment update: Qwen3-TTS now executes on CUDA with bounded CPU weight offloading, with no automatic CPU inference fallback. Earlier CPU measurements below are historical. See [qwen_gpu_integration_report.md](qwen_gpu_integration_report.md).

# Orbot voice runtime integration - 28 October 2026

## Result

The configured local pipeline completed real-device turns through native Tauri media playback. The owner subsequently confirmed: "Yes, I heard the reply." Physical audibility is therefore owner-confirmed in addition to the measured application playback; no independent acoustic instrument measurement is claimed. The owner confirmed and renamed the desired input Desktop Microphone (Realtek(R) Audio). Its device identity and label are saved in the existing AIMS writer.

Voice starts automatically, including while docked. Docking changes presentation only. Explicit Pause voice, Cancel reply and app shutdown suspend media. Clicking is a fallback/control, never required to begin speaking. The final source sends raw STT words to conversation; inferred cochlear corrections remain separately labeled observations.

## Independently observed stages

| Stage | Actual evidence | Result |
|---|---|---|
| Input device | WebView track label Desktop Microphone (Realtek(R) Audio), live capture, RMS and stable capture UUID | Verified capture; device confirmed by owner |
| Cochlear/STT | Real microphone turn reached Whisper base and existing V3 stages; raw transcript Okay on a completed turn; measured recognition 1469 ms (another turn 3000 ms) | Verified execution; semantic accuracy still depends on input/Whisper |
| Conversation and inference | Same active embodiment session, live shared llama.cpp Qwen2.5-7B-Instruct Q4_K_M, response Understood; measured inference 828 ms (another turn 875 ms) | Verified |
| Inculcation | v1.3, full digest 2a6642e90053134c6733d408344d228712f82a7b006bfa3e9878d94c14801546 | Unchanged, validated and protected |
| Qwen3-TTS | Local 1.7B CustomVoice model, Ryan, CPU; live completed synthesis measurements 73563, 69219 and 38312 ms | Verified synthesis; latency remains high |
| Tauri playback | onplaying and onended; completed output lasted 1.52 seconds; interruption event also observed | Application playback verified; owner confirmed hearing the reply |
| Full round trip | Microphone -> V3/Whisper -> active session -> llama.cpp -> Qwen3-TTS -> native WebView playback end | Application round trip verified; audible output confirmed by owner |
| Dock continuity | Three live launch/recall cycles preserved microphone capture UUID, session digest, all runtime instances, foundation digest and activation entry | Passed; voice remains available docked |

The shared llama.cpp service was never stopped or reconfigured by this work. No Windows or browser speech engine was introduced. Browser/WebView APIs supply capture, utterance segmentation and generated WAV playback only.

## Exact source changes in Spruked/Orbot

- `desktop/src/voice.ts`: continuous selected-device capture, device enumeration, automatic listening, speech boundaries, correlated HTTP abort/cancel, stale result suppression, playback/utterance interruption, resumption, media cleanup and stage/device/error reporting. Capture is reused between turns.
- `desktop/src/main.tsx`: initializes voice with runtime renderer readiness; dock/hide no longer suspends media; explicit voice control/input-selection events; existing shutdown still closes the session.
- `desktop/src-tauri/src/desktop_host.rs`: authenticated native voice controls and microphone configuration; native credentials remain outside the renderer. Recall only changes presentation.
- `runtime/communication/service.py`: correlated voice turns, authenticated cancellation/preferences/current-turn inspection, persisted microphone choice via existing HostMemory/AIMS collection, raw recognized speech used for conversation, labeled derived corrections, per-stage metrics and returned hearing/context metadata. Lifecycle readiness uses foundation preflight, not the last turn's capacity result.
- `runtime/communication/voice_turns.py` (new): volatile session/turn cancellation registry. It does not issue execution permission.
- `runtime/communication/providers.py`: bounded CPU threading and temporary cancellation hook in the configured Qwen adapter; explicitly budgeted optional retrieval based on actual llama.cpp token counts; omitted AIMS atom IDs reported. No education/history truncation.
- Tests: `desktop/tests/voice_lifecycle.test.mjs`, `runtime/communication/tests/test_voice_cancellation.py`, `test_cochlear.py`, `test_provider_memory.py`, and `runtime/tests/test_voice_diagnostics.py`.
- `scripts/verify_voice_runtime.py`: repeatable configured-service probe with ordinary temporary session and final cleanup. This probe explicitly does not claim microphone or speaker validation.

`cochlear.py` and the legacy hearing stages were inspected and reused, not replaced by another speech engine.

## Exact source changes in independent Dock repository

- `frontend/src/components/VoiceStatus.jsx` (new): live voice stage, actual microphone name, explicit input chooser, refresh, Start listening, Pause voice, Cancel reply and actionable errors.
- `frontend/src/panels/DockingBay.jsx`: embeds voice controls and status while preserving Docked/Operational and Launch Orbot wording.
- `desktop/src-tauri/src/desktop_host.rs`: bounded native commands for live voice telemetry, explicit media controls and selected-microphone application. Existing Vault credential and launch correlation are retained.
- `backend/app/services/vault_client.py`: Qwen synthesis tests allow 300 seconds and return a voice-specific failure instead of a misleading Vault error. Other routes retain their existing timeout.
- Reports and continuity/device acceptance JSON remain in Dock's own `docs/`. No repository merge, extra vault or cross-repository data owner was introduced.

## Tests and builds

| Check | Result |
|---|---|
| Communication suite | 38 passed |
| Runtime regression suite | 58 passed |
| Frontend voice/lifecycle tests | 10 passed |
| Dock backend suite | 14 passed |
| Rust invisible initial window test | 1 passed |
| Orbot TypeScript/Vite build | Passed |
| Dock Vite build | Passed, existing bundle-size advisory |
| Both native custom-protocol builds | Passed |
| Actual Dock-owned cycles with voice capture | 3 passed |

Total automated tests: 121. Tests cover cancellation without late output, raw versus inferred speech separation, auth for microphone preferences and transcript inspection, preserving the sole writer, non-destructive overflow, explicit optional-retrieval omission, continuous capture and explicit suspension.

## Failures found and resolved

1. System-default input was ambiguous. The owner renamed/confirmed Desktop Microphone; exact input selection now persists and an unavailable selected device does not silently fall back.
2. Closing/reopening capture on every short rejected utterance caused repeated retriggering. The selected stream now remains open between turns. A brief initial transient may still be rejected after application startup.
3. A first service probe required 9969 prompt tokens in an 8192-token slot because optional saved configuration was retrieved in bulk. Complete inculcation was preserved. Optional recall is now budgeted explicitly; source IDs of omitted records are visible.
4. A capacity refusal changed the old readiness flag, causing Dock's supervisor to stop runtimes. Turn-level refusal no longer changes lifecycle foundation readiness.
5. Inferred cochlear corrections could replace what the owner actually said. The final source supplies the original STT transcript and preserves corrections separately as unverified.
6. Dock's 15-second synthesis timeout was shorter than actual local Qwen performance. Its explicit synthesis test now permits 300 seconds.

## Remaining limits

- Physical speaker audibility was confirmed by the owner after the live test. Independent acoustic instrumentation was not used; native media events alone are not treated as acoustic proof.
- CPU Qwen3-TTS is too slow for fluid conversation: recent synthesis took 38-74 seconds, and the cold fixture probe took 233 seconds. The existing 8 GB GPU remains shared with the required Qwen2.5 service. No alternate voice engine or model was substituted.
- Automatic speech boundaries use energy detection, not speaker identity or a wake word. Playback interruption was observed; reliable echo rejection and whether a particular interruption came from the owner versus speaker pickup need further device testing.
- The microphone remains open during inference/synthesis, but a new utterance is not submitted while state is thinking. Explicit Cancel reply is available; spoken cancellation during processing is not yet implemented.
- Cancellation suppresses late audio/reply storage and checks between Qwen talker forwards. Current STT/inference calls, model loading and codec decoding may finish before cancellation is observed; this is not a promise of instantaneous CPU preemption.
- Full inculcation consumes most of the 8192-token per-slot window. Optional recall now has an explicit budget, but a sufficiently long active conversation still fails closed without shortening its education or silently dropping history.
- Conversation remains bounded and non-executing. Full TPC/RAL/Doctrine execution enforcement remains unintegrated; no voice text grants authority.
- Raw-transcript routing has automated regression coverage and is deployed after the live run. On the completed Okay -> Understood turn, raw and derived text were identical.

## Evidence and working trees

- `docs/voice_service_initial_failure.json`: initial overflow and actual cold fixture measurements.
- Dock `docs/voice_device_acceptance_results.json`: device/stage observations; transcript bodies are redacted with hashes. This exploratory log spans development restarts; use the separate continuity report for session assertions.
- Dock `docs/voice_docking_continuity_results.json`: actual three-cycle session/stream/foundation proof.
- Dock `docs/voice_final_deployment.json`: final runtime and selected-input status.
- `docs/voice_repository_status.json`: exact branch, modified/deleted/untracked paths and ownership for both independent repositories. Both trees were already dirty before this task; prior changes were preserved. No commits, pushes, repository merges or dependency installs were performed.
