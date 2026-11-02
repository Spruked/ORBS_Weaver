# Desktop Orbot motion runtime - pass 1

The Motion Runtime previously exposed a disabled consequential execution route and did not supply the native window with visual motion. This implementation adds a separate authenticated, presentation-only step path while retaining the disabled `/commands` boundary and `execution_authority: false`.

## Ownership and reference

- `runtime/motion/presentation.py`: destination choice, adjacent-display crossing, physical-pixel bounds, cursor proximity, velocity smoothing, acceleration limit and interaction hold.
- `runtime/motion/service.py`, `main.py`: existing credential protection, presentation health/diagnostics and quiet access logging.
- `desktop/src-tauri/src/desktop_host/presentation_motion.rs`, `desktop_host.rs`: monitor/cursor observation and the sole programmatic native window-position writer; lifecycle recall/explicit tray pause and owner drag take precedence. Manual dragging and autonomous motion both use the same serialized native position writer.
- `runtime/tests/test_presentation_motion.py`: real motion-controller tests and authenticated API boundary tests.

The separate legacy Orbot FieldMotion is `electron/src/hlsf_geometry/field_motion.js` in Spruked/Orb_Assistant_Desktop_2026. Its bounded desired velocity, acceleration cap and damping informed the elapsed-time adaptation. The currently indexed private spruked.com reference is `lib/motion_runtime/MotionRuntime.ts` at commit 5f72d64203eb9b3268fa6d2ab59e99622befb83f; it uses one position authority and suppresses ambient motion for hold/guided states. Its indexed version did not expose the exact nudge constants, so the 170/60/14 pixel and 60 px/s parameters were taken from the owner's specification. No browser ORB code or authority was copied into Desktop Orbot.

## Measured before final build

- Dock started the hidden, docked Orb and all required runtimes.
- The native presentation step path moved the visible Orb from x=26 to x=1962 across the actual 1920-pixel display boundary in about 17.1 seconds. Mean observed sample speed was approximately 113 px/s over 34 position samples. [motion_native_acceptance_results.json](motion_native_acceptance_results.json) records the measurements.
- Recall returned the Orb to Dock; its active embodiment session remained the same.
- Pointer contact caused the live controller to report interaction hold. The real Tauri button accepted a click with autonomous motion enabled.
- After replacing the prior timing-sensitive drag handler, a direct native drag moved the Orb from (529, 30) to (589, 60) with autonomous motion enabled. The controller reported interaction hold throughout; a direct click also changed the voice control state. See [motion_interaction_results.json](motion_interaction_results.json).
- The shared llama.cpp PID 11804 remained running.

## Final verification

- The final runtime reported `presentation_only`, `command_execution_enabled: false` and `execution_authority: false`.
- The final live runtime crossed the physical display boundary and selected an interior destination on the second monitor, reaching x >= 2300. See [motion_interior_acceptance_results.json](motion_interior_acceptance_results.json). A preceding live run also returned to Dock without drifting and released again with the same session: [motion_final_runtime_results.json](motion_final_runtime_results.json).
- Three additional launch/recall cycles preserved the session, cognition/communication/motion instances and professional foundation activation, while the window stayed still when docked and moved when released. See [motion_final_acceptance_results.json](motion_final_acceptance_results.json).
- Live cursor measurements: [motion_live_nudge_results.json](motion_live_nudge_results.json). One `set_position` call exists in the native writer, shared by autonomous and manual motion.
- 64 runtime regression tests and 10 frontend lifecycle tests passed. Two Rust tests passed; the desktop TypeScript/Vite build and Tauri custom-protocol build passed. The final pause-resume change also passed the 12 targeted motion/boundary/diagnostic checks.
- Dock owns startup and recall, and Desktop Microphone remained active across the tested docking cycles. The final application is released for inspection. The shared llama.cpp process stayed running.

## Boundaries and limitations

Cursor nudge uses the actual rendered orb boundary, a 170 px reach, 60 px core, 14 px direct-interaction dead zone and at most 60 px/s contribution. A controller test verifies nudge and click hold; a live native test reported a 12 px/s nudge while the window moved away from the nearby pointer. The approaching-cursor case is covered by a deterministic controller test. Ambient presentation has no authority to click, type, execute tools, or dispatch consequential motion.

The current display layout has two adjacent 1920x1080 displays at the same apparent scale and nonnegative coordinates. Negative positions, disconnected gaps, and mixed scale metadata are covered by geometry tests, not physically verified on a negative-coordinate/mixed-DPI monitor setup. Guided positioning is not implemented in this pass, so its nudge suppression could not be tested; direct interaction takes precedence.

The Orb position persists only while the native process runs; durable appearance/position preferences and window obstacle mapping were not part of this pass. Existing dirty working-tree changes were preserved. No commits or pushes were made.
