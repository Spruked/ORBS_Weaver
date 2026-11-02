# Motion Runtime Pass 3 — implementation and verification

Status: incomplete. The running Dock-owned application remains the previous build; native MORB behavior has not been verified.

## Implemented

- `runtime/motion/morb_guidance.py`: transient UUID entity identities, independent state and velocity, owner-provided physical-coordinate guidance, adjacent offset, neutral arrival pulse and timed teardown. A segment through an unmonitored gap is rejected. These identifiers are not prime signatures.
- `runtime/motion/service.py`: existing desktop credential protects assignment and clearing. Assignment requires recent presentation activity. Coordinates are explicitly labeled unverified and no desktop action is issued.
- `desktop/src-tauri/src/desktop_host/morbs.rs`: host-side transparent, click-through windows driven by scheduler state, closed on recall; separately positioned from the main Orb. No claim of verified Windows click-through or DPI behavior until tested.
- `desktop/src/main.tsx`, `desktop/src/styles.css`: neutral, pulsing 15 logical pixel core with halo and an arrival pulse; reduced-motion CSS. The MORB renderer does not initialize voice.
- `desktop/src-tauri/capabilities/morbs.json`: only event listening for guidance windows.

## Evidence and limits

- Frontend production build and Rust check succeeded; two Rust unit tests passed.
- Ten Python tests passed, including four guidance tests. Tests cover two simultaneous identities, destination/arrival state, authentication, invalid targets and disconnected displays. This is simulation, not native presentation proof.
- Dock startup/release had been checked during the preceding pass. This pass's restart attempt sent `/shutdown` twice; it returned success, but the Dock process and owned ports remained active. The existing process and shared model were preserved; this build was not substituted into the running application.
- No native visual, click-through, performance, live monitor crossing, mixed-DPI, recall/release, or voice continuity test was completed for MORBs.
- No active desktop target resolver or verified task-result event was found in this Orbot repository. Neutral guidance only: green/red verified outcomes are not connected. Explicit coordinates are not evidence of a resolved target; moving targets are not tracked.
- The legacy desktop pointer contract describes separating point from action and resolving live target geometry. It is reference material, not an active implementation in this repository. Its research-MORB prime deployment count rule is not a prime-identity assignment mechanism. Prime identity and governance integration remain open.
- Pass 2 real 3D gaze and shape assets remain unavailable, so that prerequisite is not complete.
- The owner controls have no MORB assignment UI yet. The credential-protected runtime endpoint is an integration surface, not an end-user workflow.
- Adjacent offset is relative to the supplied point, not a target bounding box; target visibility cannot be guaranteed for unknown controls. Disconnected-monitor routing is blocked rather than rerouted. Mixed-DPI sizing and hit testing require native verification.
