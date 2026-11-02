> Voice lifecycle update: docking now preserves active microphone and playback; only explicit Pause/Cancel or shutdown suspends media. Earlier suspension descriptions below are historical. See voice_pipeline_status.md.

# Dock-owned startup and continuous presentation lifecycle

Implemented October 28, 2026. The initial presentation is always docked: this is
an enforced product invariant, not an optional startup preference.

## Orbot-owned implementation

- `desktop/src-tauri/tauri.conf.json`: the Orb window is initially invisible.
- `desktop/src-tauri/src/desktop_host.rs`: initializes docked state to true,
  refuses independent launches without a matching running Dock instance, and
  keeps the initial window hidden. Release requires Dock lifecycle readiness,
  the expected Communication instance, matching foundation identities, and all
  required runtimes ready in their existing bounded modes.
- Native tray Show opens Dock; Release goes through Dock; Recall returns to
  Dock; Quit requests Dock-owned shutdown. Window close recalls rather than
  destroying the embodiment or ending the session. Native lifecycle mutations
  require the existing server-side Vault credential and matching Dock launch
  identity. That identity is correlation, not a new permission/permit.
- The renderer cannot directly show/hide/focus its window through the removed
  window permissions. Native Dock-controlled transitions own visibility.
- `desktop/src/voice.ts`: separates `suspend()` (microphone/playback interruption)
  from `endSession()`. Docking, hiding, page visibility and renderer cleanup use
  suspension; shutdown/explicit completion uses existing AIMS reconciliation.
- `desktop/src/session.ts` and `Conversation.tsx`: acquire the same runtime-owned
  embodiment session through the native bridge, keeping credentials out of the
  frontend. The separate Dock management-observation session remains separate
  from the active Orbot conversation; it is not another cognitive identity.
- `HostMemory.start_embodiment()` supplies one idempotent active session. It
  survives idle docked periods until explicit completion/shutdown. Other sessions
  retain their existing idle-expiry policy. Priority caches remain bounded.
- Authenticated `POST/GET /sessions/embodiment` expose that existing-writer
  lifecycle to the native host. `POST /lifecycle/shutdown` checks the exact
  Communication instance and completes `close_all()` before graceful server exit.
- Communication claims its exclusive loopback port before startup initializes
  AIMS. A competing launch fails before opening another writer.

The native renderer confirms its lifecycle event listeners are registered before
Dock marks the embodiment ready. Recall does not call the inculcation initializer,
create another AIMS writer, replace identity, or end the active session.

## Education revision

The product requirement is taught in
`inculcation/Desktop_ORB_Professional_Inculcation_v1.3.md`. It retains the complete
prior education and adds Dock-first startup, mandatory initial docking,
session-preserving recall, media/session separation and shared-model ownership.
Core Four and reference snapshots are unchanged. v1.2 source is retained.

The normal compiler and controlled activation process advanced 1.2 to 1.3:

```text
Previous: 5b8dd300d3bc17b63138ff2c3d06cb81fc50f7faf6747a69c8ed5d8b7ebb6775
Active:   2a6642e90053134c6733d408344d228712f82a7b006bfa3e9878d94c14801546
```

Foundation initialization/prefill occurs on cognitive-runtime startup. Attaching
to an existing ready runtime does not initialize it again. Dock/release calls
only validate existing readiness and alter presentation. Shared llama.cpp cache
eviction/restoration remains independent of docking and never grants authority.

## Dock-owned counterpart

The independent `Spruked/Orb_Dock_Station_v2.1` repository owns the startup
coordinator, native Dock lifecycle manager, docking-bay readiness UI and native
acceptance harness. Its owning report is
`docs/dock_owned_startup_implementation.md` in that repository.

Dock initializes its management API, starts or validates/attaches Communication,
Cognition/Governance and Motion, confirms the same foundation, establishes the
embodiment session, then launches the hidden Orb. Release becomes available only
after the Orb renderer is ready and its initial hidden/docked state is confirmed.
No separate user launch of the Orb or manual runtime startup is required.

On Quit, Dock's coordinator asks the Orb to finish media/session work. It closes
the embodiment session and gracefully reviews owned Communication memory before
stopping owned processes. Attached processes are left running. Unconfirmed
durable review preserves Communication instead of force-killing pending memory.
The shared model server is never started, stopped, reset or reserved by Dock.

## Build and normal launch

Use the existing installed dependencies; no installer or startup registration
was added. From the Orbot repository:

```powershell
npm --prefix desktop run build
& "$env:USERPROFILE/.cargo/bin/cargo.exe" build --features custom-protocol --manifest-path desktop/src-tauri/Cargo.toml
```

Then, from the Dock repository:

```powershell
npm --prefix frontend run build
& "$env:USERPROFILE/.cargo/bin/cargo.exe" build --features custom-protocol --manifest-path desktop/src-tauri/Cargo.toml
& .\desktop\src-tauri\target\debug\orbot-dock-station.exe
```

`custom-protocol` embeds the built frontend; a Vite development server is not
required for these executables. This build uses the local repository layout and
existing Python environments. `ORBOT_DOCK_ROOT`, `ORBOT_REPO_ROOT`, and
`ORBOT_EXECUTABLE` support explicit owner deployment paths. Missing files or
unknown port owners cause a visible startup failure, not downloads or takeover.

## Validation and limits

Current regression results: **118 tests passed** across the separate repositories.

| Owner / suite | Passed |
| --- | ---: |
| Orbot runtime Python | 53 |
| Orbot Communication Python | 32 |
| Orbot Core-4/admission | 8 |
| Orbot bridge contracts | 10 |
| Orbot voice lifecycle JavaScript | 3 |
| Orbot initial-state Rust | 1 |
| Dock backend Python | 11 |

Both native applications and both frontends build successfully. v1.3's complete
initialization template measures **7,178 tokens**, fits the existing 8,192-token
shared slot with a 384-token generation reserve, and retains its complete text.
The cold-start and pre-existing-Communication native scenarios both passed;
their Dock-owned reports are `docs/dock_lifecycle_acceptance_results.json` and
`docs/dock_lifecycle_attach_results.json`. No production memories were touched.

Python tests cover embodiment-session idempotency, docked idle continuity,
ordinary expiry, explicit closing, authentication, and instance-bound shutdown.
Three real JavaScript tests execute the compiled voice class and prove suspension
does not issue `/sessions/end`. The Rust test asserts invisible initial config.

The real native acceptance run launches the built Dock and Orb against temporary
AIMS data. It checks initial hidden/docked state, ready renderer, rejected invalid
credentials, refusal of an independent Orb launch and a competing writer, three
release/recall cycles with unchanged session/foundation/runtime identities, and
post-transition objective recall. Dock shutdown closes owned application ports;
shared llama.cpp PID remains unchanged. See the Dock-owned JSON evidence and
report for exact results, including the existing-runtime attachment scenario.

Tests do not certify every microphone/audio driver, forced OS termination or
arbitrary coordinator-crash recovery. Resource identity mismatches fail closed
rather than silently rebind to another cognitive session. The existing TPC,
sealed Doctrine, permit/execution and VIV/Mail integration gaps are unchanged;
presentation activation is not execution authorization.

No commits or pushes were made. VIV and Prime Mail source was not changed.
