# Web Weaver × ORB Weaver
## Builder's Engineering Review of Blueprint v2.1

**Reviewer:** Codex 5.6  
**Review date:** November 1, 2026  
**Reviewed artifact:** `WEB_WEAVER_ORB_WEAVER_UNIFIED_BLUEPRINT.md` v2.1 with FR-09 Pure ORB Presence and Speech-Only Interface  
**Review scope:** architectural implementability, contracts, dependencies, contradictions, tests, and delivery risks

## Review result

**Architecture:** ready for implementation planning.  
**Contracts:** materially improved and buildable as staged interfaces.  
**Repository compatibility:** not verified; the current workspace contains the blueprint artifact but no ORB Weaver implementation repository.  
**Implementation authorization:** not granted by this review.

The eight final refinements are correctly integrated without removing the Vault, Site World/Session World boundary, semantic graph, Pointer/Ping system, demonstrations, funnel intelligence, SEO feedback, accessibility, privacy, deterministic action limits, or evidence-based release gates.

The subsequent Autonomous ORB Presence Doctrine and FR-09 are accepted as architectural overrides: no permanent corner position, dock, parking state, chatbot-centered interaction, browser voice fallback, arbitrary conversational quota, rigid personality switch, text input, transcript, message history, or text-chat fallback remains authoritative.

## FR-01 — Presence before conversation

Implemented coherently. The document now defines one continuous autonomous spatial presence whose voice is a capability rather than the primary container.

Builder requirement: the runtime root must own presence, motion, attention, voice, guidance, and task state. No chat panel, chat bubble, chat icon, text input, transcript, message history, or messaging surface may exist for Weaver.

## FR-02 — Purposeful motion doctrine

Implemented. Permanent docking, stationary default behavior, and fixed corner positioning are removed. The specification permits only bounded task-related settling, followed by resumed autonomous motion.

Required implementation contracts:

- motion controller state machine with dynamic initial placement;
- target-relative placement resolver;
- protected-region collision detector;
- yield path and resume policy;
- motion amplitude and reduced-motion policy;
- evidence event for every yield, settle, interruption, and resume.

Potential implementation issue: “continuous motion” must be calibrated so it remains observable as presence without creating distraction, motion sickness, or performance cost. This is a visual verification and accessibility test requirement, not a reason to reintroduce docking.

## FR-03 — Voice-first native interaction

Implemented. The architecture now assumes explicit microphone consent followed by natural hands-free interaction. A microphone control may exist only for permission or voice recovery; it is not a chat or text-entry control. Browser-generated speech remains prohibited.

Dependencies to validate in the implementation repository:

- approved STT service or local runtime;
- approved dedicated TTS voice and WAV/audio path;
- microphone permission and lifecycle handling;
- interruption and barge-in behavior;
- autoplay and audio-focus behavior;
- transient speech-to-intent handling and retention policy; no visible transcript or message history;
- text-accessible equivalent for every voice task.

## FR-04 — Map completeness versus runtime readiness

Implemented with four independent measurements: map completeness, target readiness, guidance success, and visitor outcome.

Builder requirement: do not implement a single `verified` boolean as the whole model. At minimum, persist separate fields for inventory status, resolution status, eligibility, safety, action evidence, destination-state evidence, and visitor outcome.

## FR-05 — Continuous ORB identity

Implemented. Guide, Support, Demonstration, Sales, and Success are responsibilities of one ORB. Runtime modes are allowed as operational states, but they must not create separate identities, prompt personas, or visual bodies.

Builder requirement: mode transitions preserve ORB identity, motion continuity, Session World, dismissal state, and source authority.

## FR-06 — Contextual initiative

Implemented. Universal conversation quotas and automatic sales suppression are replaced by relevance, visitor intent, interruption history, site policy, and dismissal state.

Builder requirement: initiative decisions must be explainable from recorded evidence. A proactive event must identify why it was relevant, which target or content supported it, and why it was permitted at that time.

## FR-07 — Canonical production and recovery

Implemented. The blueprint now requires one authoritative working project, reproducible checkpoints, protected releases, recoverable backups, and no unnecessary proliferation of branches or duplicate working copies.

Delivery requirement: the actual repository workflow still needs to be identified before implementation. No branch, worktree, commit, push, deployment, or repository migration is authorized by this review.

## FR-08 — Contractual traceability

Implemented through the requirement-to-implementation-to-verification-to-acceptance record.

Builder requirement: create traceability records before closing a gate. A prose requirement without an implementation reference and evidence reference remains incomplete.

## FR-09 — Pure ORB presence and speech-only interface

Implemented as a release-blocking interface invariant.

Required runtime checks:

- the ORB body is the only persistent Weaver interface;
- natural approved voice is the only Weaver communication channel;
- the only communication text is a temporary speech bubble containing current spoken words;
- the speech bubble has no input, history, transcript, messaging, or chat controls;
- no chat window, chat bubble, chat icon, text input, message history, transcript panel, or text-chat fallback is present;
- voice unavailability produces only a non-chat status indication;
- microphone controls, if present, are limited to permission or voice-recovery behavior;
- no browser-generated voice is loaded or substituted;
- ordinary website content, forms, navigation, keyboard access, and screen-reader support remain independent and available;
- no fixed corner or stationary dock is used.

This is a structural test, not a visual preference. The implementation must fail the interface gate if prohibited nodes, labels, controls, fallback branches, or UI states exist in the rendered ORB surface.

## Implementability review

### Buildable contracts already present

- Project Brief and approval gate;
- Page Intelligence Specification;
- Site World and Session World boundary;
- Vault commercial authority;
- Pointer/Ping target record;
- target lifecycle and readiness states;
- movement arbitration and collision contract;
- Stage Governor inputs and transition matrix;
- demonstration contract;
- allowed action boundary;
- evidence event envelope;
- release report and traceability record.

### Contracts still requiring repository-specific binding

The blueprint is intentionally architecture-level in these areas. Before code changes, bind each to the existing repository:

- TPC, Correspondence Engine, Doctrine v1, and Nine-of-Clubs interfaces;
- current ORB runtime entrypoint and loader;
- existing skin asset and adapter contracts;
- local LLM, STT, TTS, and audio transport;
- Vault persistence format and migration path;
- current route and component ownership;
- analytics/event sink;
- checkout, licensing, activation, minting, TrueMark, and Alpha CertSig interfaces;
- current deployment and backup workflow.

No implementation should invent replacement interfaces while an existing owner is available.

## Required test layers

### Contract tests

- Site World cannot be mutated by Session World events.
- Commercial answers resolve to the current approved Vault record.
- Skin patches cannot alter intelligence, geometry, routes, permissions, or policy.
- LLM output cannot invent routes, prices, coordinates, or consequential actions.
- `RECOVERY_REQUIRED` cannot be selected as a safe runtime target.

### Pointer/Ping tests

- every eligible target is inventoried;
- structural, live, and cross-page map layers agree;
- target resolution works across responsive layouts and state changes;
- passive and active ping triggers are throttled and debounced;
- guidance success requires observed destination state;
- critical unresolved targets block the applicable release.

### Motion and accessibility tests

- ORB never permanently docks or becomes stationary by default;
- protected-region collision causes a yield path;
- active typing, focus, payment, consent, and assistive-technology interaction take priority;
- interrupted tasks reconcile before resuming;
- reduced-motion behavior removes travel and trails while retaining accessible guidance;
- keyboard and screen-reader access remains available for ordinary website functions and non-conversational ORB controls; no text alternative reproduces Weaver's conversation;
- continuous presence does not obstruct reading or task completion.

### Stage and initiative tests

- explicit visitor intent outranks inference;
- support blocks sales diversion while unresolved;
- stale signals decay;
- contradictory signals do not force a stage transition;
- dismissal prevents unsolicited re-entry within its scope;
- initiative events contain relevance and policy evidence.

### Demonstration and release tests

- every public capability claim has a demonstration contract;
- unavailable demonstrations produce the standardized truthful failure response;
- release evidence distinguishes movement, target verification, guidance success, and business outcome;
- footer, splash, map, voice, accessibility, and commercial-source checks are independently reported.

## Contradictions resolved in v2.1

| Tension | Resolution |
|---|---|
| Presence versus chatbot framing | One autonomous spatial presence; conversation is subordinate capability |
| Ambient presence versus no stationary behavior | Independent ambient motion with dynamic placement; only bounded task-related settling |
| Hands-free voice versus browser permission | Explicit consent is the gate; hands-free interaction is the default after consent |
| Map readiness versus outcome | Four separate measures; no percentage substitutes for critical-target or outcome evidence |
| One identity versus operational modes | Modes are internal responsibilities of one ORB, not separate agents |
| Initiative versus interruption | Contextual relevance and policy decide initiative; dismissal and active tasks take priority |
| Recovery versus repository proliferation | One canonical project with recoverable checkpoints; delivery topology follows the actual repository workflow |

## Delivery risks

1. **No implementation repository is attached to this workspace.** Existing code compatibility, package versions, runtime entrypoints, and current data contracts remain unverified.
2. **Hands-free voice depends on browser permissions, audio lifecycle, STT/TTS availability, and interruption handling.** These require real runtime tests.
3. **Continuous motion creates performance and accessibility constraints.** It needs measured frame cost, collision evidence, and reduced-motion validation.
4. **Dynamic layouts can invalidate target geometry.** Material layout changes must trigger rescan and re-verification.
5. **Commercial truth is cross-system.** Checkout, licensing, activation, minting, TrueMark, and Alpha CertSig must be bound to one Vault authority before offers are exposed.
6. **The 85% SAFE figure remains a configurable campaign-readiness metric, not a universal quality guarantee.** Critical-target blockers remain individual.

## Engineering recommendation

The blueprint is ready to become an implementation plan. The next safe engineering increment is not broad runtime construction. It is the ORBS Weaver Gate A package:

1. identify the canonical repository and runtime owner;
2. freeze the Project Brief and v1 capability boundary;
3. define the machine-readable target, event, traceability, and skin-patch schemas;
4. produce the landing-page Page Intelligence Specification;
5. bind the existing ORB runtime interfaces;
6. implement and verify the landing-page vertical slice;
7. record evidence before expanding to secondary routes.

This review finds no architectural blocker in v2.1. It does not certify implementation compatibility or authorize code changes until the canonical ORB Weaver repository and current runtime contracts are identified.
