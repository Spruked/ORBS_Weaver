# Codex VS Code Handoff

## Workspace consolidation update November 1 2026

The owner has consolidated all six component repositories into one root Git
repository. Nested Git metadata was moved outside the workspace.
`Vault-Logic-System-Template` is now `orbs_vault_system`, the system's single
source of truth. Its `AUTHORITY.md` supersedes historical component authority
claims. Existing component code is retained; this is not certification that
integration or placeholder subsystems are complete.

The owner clarified that landing-page design, complete semantic mapping, and
spatial mapping come before voice work. Design around an autonomous ORB generally
80–200 px in diameter, resizing by position and intent, with pointer/ping guidance
supporting checkout, sales, and relevant increases in order value.

## Project

This is the new from-scratch ORBS Weaver Website ORB build.

Working directory:

```text
C:\Users\bryan\Desktop\ORBS_Weaver
```

This build is independent of the old WSL repository and independent of the older `website_orb_final` implementation. Do not merge, copy, rename, or restructure the old implementation into this project unless Bryan explicitly authorizes a specific file or capability.

## Current files

```text
index.html
styles.css
assets/orb-body.svg
src/main.js
src/orb-runtime.js
docs/
```

The current local preview has been associated with `http://localhost:4173/`. Verify the active server and its owner before changing the startup path. Do not assume that this folder has npm scripts; it currently has no `package.json`.

## Read first

Read these documents in this order:

1. `docs/ORB_WEAVER_WEB_WEAVER_REVISED_MASTER_BLUEPRINT.docx`
2. `docs/WEB_WEAVER_ORB_WEAVER_UNIFIED_BLUEPRINT.md`
3. `docs/WEB_WEAVER_ORB_WEAVER_BUILDER_REVIEW.md`
4. This handoff

The DOCX is the consolidated architecture and build sequence. The Markdown files preserve the earlier unified blueprint and engineering review. The latest presence doctrine in the DOCX supersedes any older chatbot, fixed-dock, browser-voice, or text-fallback language in historical material.

## Non-negotiable product identity

Weaver is an autonomous, courteous, spatially intelligent presence inside the website.

He is not:

- A chatbot
- A chat window
- A chat icon
- A floating FAQ widget
- A fixed-corner assistant
- A stationary docked character
- A browser SpeechRecognition or speechSynthesis wrapper
- A text-chat fallback
- A transcript or message-history panel

The ORB body is the persistent interface. Voice is the communication channel. Movement, pointer, and ping are the guidance system. A speech bubble may briefly display current spoken words, but it is not a chat bubble and contains no input, controls, or history.

## Presence requirements

- Weaver moves continuously and independently.
- Movement is purposeful, polite, collision-aware, and context-sensitive.
- A Polite Nudge causes a small natural displacement without cursor following.
- Weaver yields space for reading, typing, forms, navigation, and important content.
- Movement may become subtle for a short task-related moment while speaking, listening, or pointing, but Weaver is never docked or locked.
- Guide, support, demonstration, and sales are capabilities of one continuous identity.
- Contextual initiative is allowed. Rigid conversation quotas and rigid role personalities are not the architecture.

## Voice contract

Use this path:

```text
getUserMedia
  -> MediaRecorder
  -> RMS and silence detection
  -> STT
  -> deterministic or approved answer path
  -> TTS
  -> cached audio
  -> playback
```

Rules:

- Voice is native, consent-aware, and hands-free after permission.
- A microphone control may exist only as a permission or recovery affordance.
- Do not use browser `SpeechRecognition`.
- Do not use browser `speechSynthesis`.
- Do not silently fall back to browser-generated speech.
- Use single-flight recording, STT, TTS, and playback.
- If approved speech is unavailable, show a non-chat status and preserve ordinary site functionality.

## Authority model

Keep these responsibilities separate:

```text
Site World      = governed site truth
Session World   = temporary visitor state
Vault           = authority and evidence storage
A Priori        = compiled approved knowledge
A Posteriori    = customer-isolated learning and observations
TPC and Doctrine= deterministic truth and authority boundaries
LLM/provider    = interpretation and articulation only
```

The visitor session must never rewrite Site World. The model must not invent prices, policies, routes, targets, commitments, warranties, discounts, or transaction completion. Payment completion requires authoritative observed evidence.

## Manufacturing model

The product has three distinct layers:

1. Orb Weaver manufacturer
2. Golden Website ORB template
3. Customer Website ORB

The production sequence is:

```text
Project Brief
  -> Site Intelligence Plan
  -> Full Scan Evidence
  -> Catalog / Ontology / QA / Policies
  -> Site World and Pointer Map
  -> Owner Verification
  -> Golden Template Clone
  -> Customer Data Injection
  -> Clean Customer Learning State
  -> Package and Manifest
  -> Fixture and Dry Run
  -> Website / ORB / Business Acceptance
  -> Deployment
```

The highest-priority missing foundation is the canonical Full Scan Evidence contract. Every compiled artifact must retain provenance, confidence, source URL, timestamp, content hash, verification state, conflict information, and compiler version.

## Pointer and ping contract

Every eligible target is inventoried. Inventory completeness, verification, runtime readiness, guidance success, and business outcome are separate measurements.

Targets must be attached to live elements, not fixed screen coordinates. Verify:

- Target identity
- Route and section
- Visibility
- Enabled state
- Semantic meaning
- Responsive geometry
- Scroll and sticky behavior
- Modal state
- Keyboard accessibility
- Observed result after guidance

Use explicit recovery states such as `NEW`, `VERIFIED`, `RECOVERED`, `OWNER_VERIFIED`, `DEPRECATED`, `REMOVED`, and `RECOVERY_REQUIRED`. A recovery-required target blocks pointer action but does not disable Weaver's voice or knowledge.

## Build sequence for this new project

### Step 1 Inspect the existing slice

Read the current HTML, CSS, `src/main.js`, and `src/orb-runtime.js`. Identify what is already visible and running. Do not replace working files blindly.

### Step 2 Establish the first Page Specification

Define the landing page Purpose, Objective, Intended Outcome, audience, content, semantic targets, ORB knowledge, guidance targets, demonstration moment, next sales step, and acceptance evidence.

### Step 3 Complete the landing vertical slice

The first build must prove:

- Shared layout and authoritative signature footer
- Semantic HTML and structured data
- ORB presence and autonomous movement
- Voice permission and approved voice path
- Temporary speech bubble only
- Pointer and ping to one verified target
- Honest failure and recovery state
- Responsive and accessible behavior

### Step 4 Add the intelligence contracts

Implement the smallest machine-readable versions of:

- Site World
- Session World
- Full Scan Evidence
- Pointer Map
- Demonstration Contract
- Stage Governor state
- Unified event schema

Use local fixtures first. Do not claim a full manufacturing system until a fixture passes the entire scan-to-package path.

### Step 5 Add pages one at a time

Build secondary pages sequentially. Each page requires its own Page Intelligence Map, verified targets, purpose, objective, intended outcome, demonstration, and next step. Merge maps into the site-wide Master Pointer and Ping Map only after verification.

### Step 6 Add the standard splash last

The signature splash is designed once on the reference ORBS Weaver site after the autonomous presence is complete. Later sites install the approved standard; they do not redesign it independently.

## Acceptance gates

```text
Gate A  Project Brief approval
Gate B  Site Intelligence Plan and Vault initialization
Gate C  Landing vertical slice
Gate D  Evidence and compilation
Gate E  Pointer and voice runtime
Gate F  Journey and demonstrations
Gate G  Packaging and fixture validation
Gate H  Website, ORB, business, privacy, and release acceptance
```

No readiness percentage can excuse an unresolved critical target. A release requires evidence from three layers:

- Website: layout, accessibility, routes, forms, SEO, and footer
- ORB: voice, movement, collision, pointer, ping, recovery, and state transitions
- Business: approved offer, price source, objection answer, conversion path, and delivery capability

## Scope boundaries

Do not expand the first build into:

- The old WSL repository
- The old `website_orb_final` codebase
- Electron or DockStation integration unless specifically authorized
- Meta or Messenger adapters
- Hardware or drone ORBs
- Enterprise process scanning
- CRM or marketplace integrations
- Unverified marketing or investor claims

## Handoff working rules

- Preserve the new build as a clean from-scratch implementation.
- Do not modify WSL.
- Do not introduce a chatbot interface under another name.
- Do not add fixed-corner docking or a stationary rest state.
- Do not add browser-generated speech.
- Do not invent prices, policies, routes, targets, or completion states.
- Keep engine responsibilities separate from website content.
- Record unresolved ideas in a backlog instead of silently changing the architecture.
- Verify the visible result at `http://localhost:4173/` after runtime changes.
- Report what is implemented, what is simulated, and what remains unverified.

## First task for the VS Code Codex

Audit the five current build files and produce a read-only implementation status against this handoff. Then implement only the next approved increment: the landing-page vertical slice and its first verified pointer/ping path. Do not begin secondary pages or manufacturing compilers until the landing slice passes its acceptance checks.

## Completion definition

This project is not complete because it builds or starts. An increment is complete only when the visible behavior, runtime behavior, evidence, responsive behavior, accessibility behavior, and authority boundaries all pass the applicable gate.

Final operating sequence:

```text
Map -> Verify -> Move -> Speak -> Guide -> Support -> Demonstrate -> Sell -> Confirm
```
