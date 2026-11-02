> Voice lifecycle update: docking now preserves active microphone and playback; only explicit Pause/Cancel or shutdown suspends media. Earlier suspension descriptions below are historical. See voice_pipeline_status.md.

# Dock-first startup and activation: intended lifecycle versus current code

**Superseded source trace:** the gaps below describe the pre-implementation
inspection. Dock-owned startup, mandatory docked-first presentation and continuous
session handling have now been implemented. See
`dock_owned_lifecycle_implementation.md` and the Dock-owned native acceptance
reports for current code and measured outcomes. This historical trace remains
as the before-state, not the current implementation status.

Owner correction recorded October 28, 2026. This supersedes earlier descriptions
that treated independent manual Orbot launch as the intended deployment.
This is a source trace and documentation correction, not a startup implementation
or a newly passed native lifecycle test.

## Intended lifecycle

1. Dock Station starts and initializes its management environment.
2. Dock launches Orbot and connects it to the existing runtimes and Vault/AIMS.
3. Orbot's initial presentation state is docked, every time.
4. Dock activates/releases the already initialized Orbot into its floating Tauri
   embodiment after the required runtime/foundation readiness checks.
5. Docked/floating transitions retain cognition, identity, memory and the active
   session. A presentation transition is not a session-completion event.
6. Tray controls manage windows and the running application's lifecycle.

The protected foundation initializes for the cognitive runtime, not on each
dock/undock transition. Integrity validation and restoration after actual context
loss remain necessary; presentation changes do not create new education instances.
Presentation activation grants no execution permit or new authority.

Separate repositories and executable processes remain compatible with this
Dock-owned launch sequence. They do not imply independent user launch or separate
cognition/vault ownership. The shared llama.cpp service remains shared.

## Trace from Dock outward

Paths in the Dock column are relative to the independent Dock repository; Orbot
paths are relative to this repository.

| Boundary | Current source evidence | Finding |
| --- | --- | --- |
| Dock entry | Dock `desktop/src-tauri/src/main.rs`: `run(Role::Station)` | Starts the Station host |
| Management initialization | Dock `tauri.conf.json`: `beforeDevCommand` starts frontend Vite; Dock `frontend/src/App.jsx` starts a management AIMS session after login | No native setup path was found that launches the owner API backend |
| Orbot launch | Dock `desktop_host.rs`: `peer_status`, `dock_orbot`, `undock_orbot` only send requests to existing peers | No Orbot executable launch or supervisor spawn found; absent peer yields a message asking for the other application to start |
| Runtime startup | Orbot `runtime/supervisor.py:main()` launches Communication, Cognition/Governance and Motion | Standalone entrypoint; Dock does not invoke it. Its preflight rejects occupied runtime ports rather than attaching to existing runtimes |
| Orbot native entry | Orbot `desktop/src-tauri/src/main.rs`: `run(Role::Orbot)` | Separate executable entry; Dock ownership is not enforced |
| Initial dock state | Orbot `desktop_host.rs:run()`: `AtomicBool::new(false)`; `tauri.conf.json`: Orb `visible: true` | Starts floating, conflicting with required docked-first behavior |
| Release/return | Native `/undock` shows the Orb and sets docked false; `/dock` hides it and sets docked true | Existing process/window is reused, but no cognitive readiness gate is consulted |
| Dock bay | Dock `frontend/src/panels/DockingBay.jsx` polls existing Orb status and invokes cosmetic commands | Waits for Orbot; does not launch it. A displayed docked image is not evidence of runtime initialization |
| Foundation | Orbot `runtime/communication/service.py:initialize_memory()` and `memory.py:get_memory()` | Validates complete education, binds existing AIMS writer, requests model prefill on runtime initialization |
| Foundation reuse | Orbot `inculcation.py:FoundationLoader.load()` and `HostMemory.bind_professional_foundation()` | Same validated snapshot/digest is reused; same-process AIMS rebinding is idempotent |
| Window transitions versus foundation | Both native `desktop_host.rs` implementations only show/hide windows and update presentation state | No dock/undock call reinitializes foundation, restarts a runtime or opens an AIMS writer |
| Orb voice continuity | Orbot `desktop/src/main.tsx:dock()` calls `voice.cancel()`; `voice.ts:OrbVoice.cancel()` POSTs `/sessions/end` and clears its session | Explicit return-to-Dock path ends voice session: conflicts with required continuity |
| Hidden-window behavior | Orbot `main.tsx` cancels voice on `document.hidden`; `Conversation.tsx` ends its session on pagehide/close | Presentation, media interruption and session completion are not fully separated. Whether native hiding emits those browser events needs live testing |
| Cross-surface session binding | Dock `frontend/src/services/api.js` owns `aims_session`; Orb voice owns another private session ID; Conversation owns a separate ref | No single active conversation-session handoff between Dock and floating presentation was found |
| Tray lifecycle | Native menus call `show`, peer `/undock`, or local `app.exit(0)` | Window controls exist; coordinated Dock-owned startup/shutdown is not implemented by these handlers |

## Verification outcome

**Not implemented:** complete Dock-owned launch, runtime discovery/attachment,
docked-first initial state, readiness-gated release and reliable active-session
continuity across presentation transitions.

**Partially implemented:** show/hide docking, bay status and tray controls reuse
native processes, but their lifecycle ownership and session handling do not yet
match the intended sequence.

**Compatible foundation behavior:** the runtime's protected education does not
depend on docking. Existing presentation handlers do not reinitialize it.
The earlier foundation/HTTP tests did not verify Dock-owned startup or native
dock/undock session continuity and must not be represented as doing so.

## Repository ownership and next implementation boundaries

- Dock owns startup/activation orchestration, management readiness, initial
  docking request and tray coordination in its repository.
- Orbot owns its startup presentation contract, readiness evidence and separation
  of stopping audio from completing the conversation session. Its existing
  runtimes and AIMS remain the cognition/memory authority.
- A launch/release integration must verify the identity/readiness of existing
  services and preserve an already running runtime/session. It must not open
  another AIMS writer or restart shared llama.cpp as a docking operation.
- Native acceptance must trace the same runtime instance, foundation digest,
  activation record and active session across initial dock, release and return;
  also verify cancellation, failed startup and actual application shutdown.
- The next controlled education revision should explicitly teach Dock-first
  launch and session-preserving presentation changes. The activated v1.2 source,
  compiled artifact and digest were not silently rewritten by this correction.

No runtime code, activation files, processes, permissions or repository ownership
were changed by this verification. Implementation requirements are now explicit;
they remain separate from the completed professional-foundation lifecycle work.
