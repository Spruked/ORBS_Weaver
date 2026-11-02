# Orbot implementation and wiring plan

Status: implementation sequence. Three process entrypoints and supervision now exist; see `runtime/README.md` for implemented boundaries and remaining work. The three runtime directories in
`structure_tree.txt` are a target layout, not implemented capabilities.

Desktop presentation has its own `desktop/` React/Vite app and Tauri 2 Rust host.
Orbot starts as a floating transparent orb with a conversation window. The dock
station is a separate sibling application, `../Orb_Dock_Station_v2.1/`, outside
this repository. Both native builds pass. The desktop has no execution authority;
memory access goes through Communication to AIMS. See
`desktop_docking_and_memory.md` for docking and session memory rules.

## Outcome

The orb is Orbot's provider-agnostic embodiment. Deterministic cognition and
governance remain the authority path; local or optional remote language models
provide advisory reasoning and conversational expression. The initial
`runtime/communication/` slice connects the existing llama.cpp endpoint on port
16520 to the desktop Conversation panel, with a separate Qwen3-TTS voice adapter
on the loopback communication service at port 16521. It does not implement the
full governed execution loop or grant tools/motion authority.

Build one machine with three independently scheduled runtimes: Motion,
Cognition/Governance, and Communication. Preserve TTI (True Technical
Intelligence), RAL (Real-Time Agency Loop), and Core-4: Kant, Locke, Hume,
Spinoza. Intent is autonomous; consequential execution is deterministically
bounded. Runtime work responds to events and actual state, rather than a fixed
sequence of scripted tasks.

The repository root is `C:/Users/bryan/Desktop/Orbot/Orbot/`.
`Orbot_Vault-Logic-System/` is the single authoritative system of record for
policy, authority, committed evidence, execution permits, and verified state.
Its AIMS Vault owns durable evidence; indexes, SKGs, and World State snapshots
are projections with explicit provenance and rebuild rules. An immutable record
that a claim was made does not establish that the claim is true.

## Ownership and runtime boundaries

| Component | Owns | Boundary |
| --- | --- | --- |
| Cognition/Governance | RAL, proposals, Core-4 evaluation, admission decisions, scheduling, tools, correspondence assessment | Requests permits and verified commits through the Vault authority interface; cannot bypass it |
| Motion | Physical and pointer execution, live reflex checks, actuator watchdogs, motion receipts | Executes only the exact permitted primitive against current state; independent emergency stop remains available |
| Communication | Authenticated ingress, event delivery, text/audio input, speech output, transport adapters | Carries authority evidence; cannot grant authority or turn an incoming message into an executable command |
| Orbot Vault Logic System | Canonical schemas, policies, grants, permit registry, immutable evidence, verified state commits | One authoritative write path; consumers use clients rather than independent authoritative stores |
| TPC | Candidate reasoning and structured evaluation through a bounded adapter | Advisory results; no implicit consent, authority grants, or independent truth promotion |
| Correspondence Engine | Evidence normalization, correspondence assessment, contradiction signals | Returns evidence and assessments; no independent action authorization or canonical memory ownership |
| TanStack application | Human input, inspection, authority controls, live status | Server verifies identity and scope; client values cannot establish authority |
| Tauri desktop | Floating Orbot embodiment, conversation, native window lifecycle | Connects through Communication; cannot issue permits, bypass admission, or own canonical state |
| Separate Dock Station | External tray application, docking bay, configuration presentation | Source remains outside this repo; AIMS owns durable data and session memory |

Vault services are the shared foundation hosted with Cognition/Governance in
the initial local deployment. They are not a fourth action runtime. Motion and
Communication access that foundation through authenticated, versioned APIs;
they never open competing writers to its ledgers. A sole writer serializes
mutation. Failure or loss of the authority service stops new normal execution.

Emergency-stop and watchdog behavior must continue when cognition, storage,
the UI, or the message bus fails. Hardware safety remains independent of all
three software runtimes.

## Wiring

```text
Human / sensors / external clients
  -> Communication: authenticate, validate, classify intent or observation
  -> Vault: record ingress provenance; retain observations as observations
  -> Cognition/Governance: read versioned World State and active goal
  -> Intelligence/TPC adapters: propose candidate primitives
  -> Core-4: Kant -> Locke -> Hume -> Spinoza ranking
  -> Hard Admission: capability, parameters, authority, target, policy, conflicts
  -> Vault authority: bind and register a short-lived execution permit
  -> Scheduler: resolve dependencies and acquire resources
  -> Communication transport: deliver the bound execution envelope
  -> Motion / speech / tool worker: verify permit and live conditions
  -> Execution receipt and independent observations
  -> Correspondence adapter: compare expected and observed effects
  -> Vault verified commit: append evidence and advance state atomically
  -> New World State event -> RAL reassessment
```

The arrows show causal boundaries, not a required global lockstep loop. Speech,
motion, observation, and tool work can overlap when dependencies and resource
ownership allow. Delivery acknowledgements and worker completion do not count
as verified effects. Internal telemetry and emergency safety signals use scoped
system channels; they do not require an ordinary action permit to report a
failure or stop an actuator.

## Phase 0 â€” Establish a reproducible baseline

1. Inventory actual files against the proposed tree; identify existing,
   migration, replacement, and new modules without creating empty scaffolds.
2. Restore missing script imports and make the existing application checks
   runnable. Check dependency and Python-version compatibility before adding
   packages. Record existing failures separately from new regressions.
3. Verify ignore rules cover local secrets, environments, generated output,
   Python caches, and runtime data throughout the consolidated repository.
4. Document one supported Windows development environment and reproducible
   commands for each current component. Preserve existing working entrypoints
   until replacements pass compatibility checks.

Exit: baseline results and migration map are recorded; no unresolved import
errors are hidden by passing substitute tests.

## Phase 1 â€” Define one contract and authority foundation

1. Put versioned canonical schemas under
   `Orbot_Vault-Logic-System/contracts/`; generate language bindings from those
   schemas rather than hand-maintaining competing contracts.
2. Define identifiers and correlations for intent, cycle, proposal, primitive,
   execution, permit, receipt, observation, and correspondence result.
3. Define event schema version, authenticated producer, sequence, correlation,
   causation, timestamp, idempotency key, deadline, and payload size limits.
4. Establish protected policy classes and doctrine integrity verification.
   Derive the doctrine hash from the actual canonical text. Missing or invalid
   policy fails closed for consequential work.
5. Define scoped authority grants, expiry, revocation, operator identity, and
   privileged audit records. Risk, confidence, truth, and authority remain
   separate values.
6. Bind permits to the canonical primitive payload digest, capability and
   adapter version, actor, proposal, World State version, authority grant,
   target, constraints, resource scope, issue time, expiry, and execution ID.
7. Use an authenticated authority lookup with atomic execution claims for the
   first implementation. Invented identifiers, altered arguments, revoked
   grants, expired permits, and replayed executions must fail verification.
   Do not invent a custom cryptographic signature scheme.

Exit: Python and TypeScript validate the same fixtures; mismatched payloads,
missing policy, insufficient authority, expiry, revocation, and duplicate
execution claims are rejected.

## Phase 2 â€” Make the Vault the operational source of truth

1. Integrate AIMS through its existing memory interface and preserve its
   immutable Vault semantics and three derived SKG domains.
2. Implement a serialized authority service and a World State reducer with
   explicit distinction between candidate observations and verified facts.
3. Persist evidence before acknowledging a committed transition. Use version
   preconditions to reject stale concurrent updates. Define crash recovery
   across permit issuance, execution claims, receipts, and verified commits.
4. Rebuild indexes and snapshots from canonical evidence. Keep secrets out of
   event payloads and define bounded retention for transient telemetry.
5. Replace TPC and Correspondence private authoritative stores with adapters
   to the Vault. Local computation caches remain derived and disposable.
6. Prove backup, restore, restart/replay, and corruption detection before using
   the integrated store for consequential operation.

Exit: one write path, deterministic replay, no promotion of unsupported claims,
and no successful acknowledgement when persistence failed. AIMS retains its
prototype maturity label until its stated hardening gates are demonstrated.

## Phase 3 â€” Run three supervised runtimes locally

1. Build lifecycle, health, startup readiness, bounded queues, and graceful
   shutdown around the three runtime entrypoints.
2. Use a local transport adapter first. Keep envelope semantics compatible
   with future separate processes and NATS; do not require a broker for the
   first working loop.
3. Start authority storage first, then validated communication, then consumers.
   Declare readiness only after schemas, policy, grants, and adapters validate.
4. On restart or disconnect, fence the previous runtime session, stop affected
   lanes, discard stale buffered commands, and require fresh state and permits.
5. Add backpressure, deduplication, cancellation delivery, and failure handling.
   Automatic retries must not repeat an uncertain external effect. Reconcile
   using receipts and observations; mark unresolved outcomes explicitly.

Exit: three runtimes start, exchange correlated events, stop cleanly, and refuse
stale or duplicate work after a simulated disconnect or restart.

## Phase 4 â€” Complete Cognition/Governance

1. Migrate the useful `runtime/cognition_governance/ral_core/` contracts and controls into the new
   ownership model. Retire the old path only after behavior is verified.
2. Make RAL event-driven with bounded concurrency, goal state, observation
   requests, and explicit defer/replan/ask/reject outcomes.
3. Keep Core-4 jurisdictions distinct: Kant checks legality and authority;
   Locke checks empirical grounding; Hume checks uncertainty and risk;
   Spinoza ranks surviving choices for coherence and goal alignment.
4. Repair Correspondence imports, constructor arguments, EvidenceItem input,
   and result types. Exercise its real entrypoint rather than a test substitute.
5. Remove TPC's fabricated consent, rights, evidence, and integrity facts.
   Missing facts remain unknown. Recheck invariants after synthesis; a failed
   contract cannot return an executable admission.
6. Require hard admission to resolve real capabilities and validate arguments,
   destructive-action policy, targets, dependencies, resources, and authority.
7. Fix order-insensitive text representations before treating TPC similarity
   as evidence of equivalent meaning. Keep reasoning output advisory throughout.

Exit: missing evidence triggers observation or deferral; forbidden actions and
failed invariants cannot reach permit issuance. Changing intelligence adapters
does not change the authority path.

## Phase 5 â€” Complete bounded execution

1. Implement dependency scheduling, resource arbitration, and active
   cancellation across tool, motion, pointer, and speech lanes.
2. Validate permits at dequeue and immediately before each external effect.
   Recheck target validity, World State, authority, and safety during continuing
   actions. Use monotonic local deadlines with explicit clock-skew policy at
   process boundaries.
3. Begin Motion with a simulator. Migrate the useful ROS bridge mappings behind
   a real adapter; revalidate buffered motion at flush time and block stale
   command state after reconnect.
4. Implement cancellation acknowledgement, bounded stop latency, actuator
   watchdogs, and an emergency-stop path that cannot be repurposed to bypass
   normal execution checks.
5. Restrict tool capabilities to explicit adapters and execution scopes.
   Record started, completed, failed, cancelled, timed-out, and unknown outcomes.

Exit: expiry, world changes, revoked authority, resource conflicts, queue delay,
active cancellation, and disconnects stop or reject work predictably. Emergency
stop works with cognition unavailable.

## Phase 6 â€” Close the correspondence loop

1. Attach observable expected effects to each consequential primitive.
2. Collect observations independently of the executor's success claim and
   preserve their source, time, uncertainty, and causal relationship.
3. Compare expected and observed effects through the Correspondence adapter.
   An SKG rejection, contradiction, or absent evidence must affect the result.
4. Submit results to the Vault commit gate: verified, contradicted, unknown,
   or partial. Only justified transitions advance authoritative World State.
5. Feed outcomes back into RAL and AIMS without treating relevance feedback
   or repeated assertions as proof of truth.

Exit: a command reporting success with no observed effect cannot mark the goal
complete; contradictory evidence causes reconciliation or replanning.

## Phase 7 â€” Make the machine inspectable and usable

The initial desktop shell is in `desktop/`. Extend it with authenticated runtime
events and controls through Communication. The Rust host currently exposes only
window controls; add narrowly scoped runtime commands when their contracts and
authorization checks are implemented. UI animation must reflect observed runtime
events rather than inventing listening, reasoning, or execution activity.

1. Replace the download-only landing page with runtime status and a live
   execution timeline while preserving TanStack Start routing conventions.
2. Expose World State version, provenance, active grants, permit status,
   Core-4 decisions, queue state, receipts, and correspondence results.
3. Add authenticated goal input, cancellation, and scoped authority controls.
   Validate all mutations server-side; never accept browser assertions of grants.
4. Add text communication first, then transcription, synthesis, and playback
   through interchangeable speech adapters. Apply interruption and permit
   rules to user-facing output and external sends.
5. Generate downloadable artifacts from tested canonical code if downloads
   remain useful; remove manually maintained runtime copies under `public/`.

Exit: an operator can explain why an action ran, identify its authority and
evidence, cancel it, and inspect its actual result from the UI.

## Phase 8 â€” Harden and extend

1. Add NATS delivery once local contract and recovery tests pass. Broker state
   is transport/replay infrastructure, not a competing authority database.
2. Add real ROS and desktop adapters individually with simulator-backed
   conformance tests and explicit capability scopes.
3. Measure latency, queue depth, stop latency, replay time, storage growth,
   throughput, and memory use. Publish operating limits from measurements.
4. Exercise process crashes, authority loss, clock skew, malformed envelopes,
   compromised publishers, duplicate deliveries, corrupted storage, and restore.
5. Align release claims with the AIMS hardening contract and demonstrated
   system behavior. Keep hardware commissioning separate from simulator success.

Exit: the supported deployment envelope is reproducible, observable, recoverable,
and backed by measured failure behavior.

## First working milestone

One local command starts the three runtimes and Vault foundation. An operator
submits a goal through Communication. Cognition reads verified simulator state,
proposes a permitted simulated movement, and dispatches it to Motion. An
independent simulator observation confirms the effect. Correspondence submits
the result, the Vault advances World State, and the UI displays the full trace.

The same demonstration must reject expired permits, altered arguments, invented
permit IDs, insufficient authority, stale state, and duplicate execution. A
second run must cancel an active movement; a restart must reconstruct committed
state without repeating an uncertain action. The simulator fixture is a test
harness, not the production decision policy.

## Implementation discipline

Build each phase as a working vertical slice. Add files when their behavior is
implemented, rather than generating the entire proposed tree as placeholders.
Keep a migration map from old entrypoints to new owners, avoid duplicate Core-4
authority paths, and update `structure_tree.txt` as decisions become concrete.

Run targeted Python contract/integration tests and frontend typecheck/build for
affected changes. Inspect build scripts before running them because the current
build includes database migration. Use an isolated test database for validation.
Do not commit, publish, push, or change GitHub state without user instruction.

The first implementation task is Phase 0 followed by the canonical contracts
and permit authority slice in Phase 1. No runtime behavior is changed by this plan.
