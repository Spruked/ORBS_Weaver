# Web Weaver × ORB Weaver
## Unified Site Intelligence, Design, and Production Blueprint

**Version:** 2.1 — FR-09 interface invariant November 1, 2026  
**Reference implementation:** ORBS Weaver — `www.orbsweaver.com`  
**Status:** Unified architectural standard and production sequence

This document consolidates the seven submitted outlines into one architecture. Repeated statements are merged. Conflicting or overly broad proposals are resolved in favor of verifiable behavior, local-first operation, operator sovereignty, visitor control, and the established Web Weaver rules.

---

## 1. The governing principle

A Web Weaver site is not a collection of pages with a chatbot attached. The ORB is a continuous spatial intelligence: one autonomous, polite, courteous presence whose voice, guidance, support, demonstration, and sales capabilities operate within the site's structured environment.

The visitor must always be able to use the site without the ORB. The ORB then adds a persistent, spatially aware intelligence layer that can:

1. orient the visitor;
2. explain the current page and its content;
3. locate and verify relevant targets;
4. demonstrate real capabilities;
5. resolve support friction;
6. explain approved offers and objections; and
7. guide the visitor toward a legitimate next action.

The central production chain is:

```text
Approved content
  → Site World
  → semantic and navigation graph
  → Pointer/Ping Master Map
  → governed ORB guidance
  → verified visitor outcome
  → measured improvement
```

The ORB cannot reliably sell what it cannot find, support what it cannot understand, or claim success where the target and outcome were not verified. Guidance and governance are distinct: governance constrains claims and consequential actions; guidance determines how the ORB moves, attends, explains, and assists.

---

## 2. Non-negotiable Web Weaver rules

### Rule 1 — Signature footer on every public page

Every public page displays:

> Built with the Power of Web Weaver A product of Pro Prime Series AI LLC © 2026 Pro Prime Series AI LLC. All rights reserved.

Implementation requirements:

- one shared footer component in the global layout;
- wording stored in one authoritative constant;
- no route may opt out;
- real readable text, never hidden by motion, overlays, or the splash;
- coverage checked before build and deploy, after deploy, and daily with timestamped PASS/FAIL evidence;
- missing or failed coverage blocks release until corrected.

### Rule 2 — Landing page first; signature splash last

- Build and accept the landing page before subsequent pages.
- Do not create a collection of unfinished placeholder routes.
- Design and ratify the signature splash once on the ORBS Weaver reference site.
- Later Web Weaver sites install the approved, versioned splash package; they do not redesign it unless a new global version is approved.
- First-time visitors receive the full splash.
- Returning visitors receive a Skip control and no additional interruption.
- Reduced-motion visitors receive a non-animated version of the same branded opening.

### Rule 3 — Complete Pointer/Ping mapping

Every page receives a comprehensive Page Intelligence Map while it is built. The map includes every eligible target and guidance opportunity, even when runtime conditions mean Weaver will not use all of them.

Runtime selection is conditional; mapping is comprehensive.

### Rule 4 — Purpose, objective, intended outcome

Every page defines these before construction:

- **Purpose:** why the page exists and what value it provides;
- **Objective:** what the page must accomplish;
- **Intended outcome:** the measurable visitor result or action;
- **Success evidence:** how the outcome is verified.

### Rule 5 — ORB-native construction

Every page, section, control, and content relationship must be understandable to both humans and Weaver. The ORB is not permitted to become the only way to access important information.

### Rule 6 — One page at a time

Each page is designed, implemented, mapped, verified, and accepted before the next page advances.

### Rule 7 — Verifiable guidance

Weaver resolves a target and verifies the resulting state before guidance counts as successful. An attempted animation is not evidence of completion.

### Rule 8 — Governed support and sales

Weaver operates only from approved facts, policies, offers, prices, objections, routes, and actions. It does not invent claims, negotiate, or make commitments outside its authority. Proactive sales posture, checkout presence, initiation limits, and stage model are explicit per-site policy parameters in the Project Brief; they are not silently standardized by the compiler.

### Rule 9 — Search-first discoverability

Every indexable page has a crawlable, accessible, technically sound foundation independent of ORB speech or animation.

### Rule 10 — Evidence-based release

Build completion, a successful launch command, or a passing compile is not product completion. Release requires website, ORB, and business acceptance evidence.

### Rule 11 — Reusable engineering

Verified components, maps, tests, schemas, scripts, and release checks become reusable Web Weaver assets.

### Rule 12 — Living specification

The blueprint evolves through explicit, recorded changes. New ideas go to the Backlog unless they are approved into the active scope.

### Rule 13 — Pure ORB presence and speech-only interface

Weaver's body is the interface. His natural voice is the communication channel. His movement, pointer, and ping are the guidance system. The only text associated with Weaver's communication is a temporary speech bubble displaying his current spoken words.

| Interface element | Requirement |
|---|---|
| ORB body | Primary and persistent interface |
| Autonomous movement | Continuous, natural, independent, and courteous |
| Voice | Natural speech through approved synthesis |
| Listening | Voice-first and consent-aware |
| Speech bubble | Temporary display of current spoken words only |
| Pointer and ping | Spatial guidance to verified targets |
| Chat window | Prohibited |
| Chat bubble or chat icon | Prohibited |
| Text input box | Prohibited |
| Message history or transcript panel | Prohibited |
| Text-chat fallback | Prohibited |
| Stationary dock or fixed corner | Prohibited |
| Browser-generated voice | Prohibited |

The speech bubble is not a chat bubble. It has no input field, history, transcript, chat controls, or messaging behavior. It appears while Weaver speaks and disappears naturally when the speaking interaction concludes. If approved speech synthesis is unavailable, Weaver reports the limitation through a non-chat status indication and does not create a replacement conversation mechanism. Ordinary website content, forms, navigation, and accessibility accommodations remain available; this rule governs Weaver's interface.

---

## 3. Architectural model

### 3.1 The four operational layers

#### Layer 0 — Vault System: authoritative truth

The Vault is the sole authoritative storage boundary for a Site World and its governed evidence. The conceptual layout is:

```text
vault_system/
└── clients/<domain>/
    ├── site_worlds/
    ├── raw_artifacts/
    ├── pointer_maps/
    ├── intelligence_packs/
    ├── customer/
    ├── sessions/
    ├── releases/
    └── backups/
```

The Vault contains source scans, approved content, Site World versions, maps, intelligence packs, customer/session records, checkout or licensing records, reports, release evidence, and rollback references.

There is one source of commercial truth. Prices must never be duplicated into stale page copy or independently maintained ORB prompts.

#### Layer 1 — ORB Weaver Intelligence Engine

The intelligence engine builds and updates the Site World. It may include:

- sitemap discovery with depth, delay, and robots awareness;
- on-page and technical SEO inspection;
- SSL, robots, sitemap, schema, redirect, broken-link, CMS, and checkout detection;
- semantic and entity extraction;
- page-purpose and funnel classification;
- content, FAQ, objection, proof, and offer indexing;
- SEO, performance, accessibility, mobile, security, and content scoring;
- intelligence-pack generation with source citations.

Scanning creates candidates and knowledge. It does not grant runtime permission to act.

#### Layer 2 — Pointer/Ping Master Map

The Master Map is the verified spatial and semantic model of the site. It contains:

- page and route records;
- section and content nodes;
- semantic target records;
- pointer geometry;
- ping geometry;
- state and eligibility conditions;
- route and return-path relationships;
- verified guidance candidates;
- failure and recovery policies.

The map is the site's LiDAR-like guidance layer. A **pointer** is a semantic, navigable target. A **ping** is an active signal that tests or communicates the target's relevance and readiness.

Each target moves through a lifecycle gate:

```text
UNCERTAIN → SAFE
     │
     └────→ RECOVERY_REQUIRED
```

`SAFE` means the target is resolved and eligible for the relevant action. `UNCERTAIN` means it requires context or additional verification. `RECOVERY_REQUIRED` blocks dependent guidance and release paths until corrected or explicitly excepted.

The initial release threshold should be configurable. The reference standard uses **more than 85% SAFE** for campaign readiness, while any unresolved critical target remains a release blocker regardless of the aggregate percentage.

#### Layer 3 — ORB Guidance Runtime

The runtime renders Weaver, reads the current Session World, selects an authorized guidance candidate, and executes only permitted actions.

The runtime includes:

- visual presence and skin rendering;
- page-load and viewport awareness;
- movement and obstacle avoidance;
- text and voice interaction;
- guide, support, and sales behaviors;
- controlled scrolling, highlighting, navigation, and form assistance;
- demonstration orchestration;
- session continuity across pages;
- outcome verification and event logging.

Governance, the Stage Governor, the action resolver, and verification are cross-cutting controls over all four layers.

### 3.2 Site World and Session World

The architecture keeps durable site knowledge separate from volatile visitor state.

**Site World** describes what the site contains:

- pages and routes;
- approved content, offers, prices, policies, and objections;
- semantic entities and relationships;
- target maps and live-resolvable geometry;
- navigation graph and legal transitions;
- demonstrations, tours, proof, and support paths;
- approved guidance patterns and source citations.

**Session World** describes what is true for one visitor now:

- current route, viewport, and page state;
- declared or inferred visitor intent;
- pages and targets visited;
- questions asked and unresolved;
- active funnel stage;
- hesitation, friction, or completion signals;
- completed guidance evidence;
- permissions and available actions;
- user preferences such as reduced motion or minimized ORB.

The ORB uses both worlds, but Session World cannot rewrite Site World without an approved learning or content workflow. The visitor encounters one continuous ORB identity across Guide, Support, Demonstration, Sales, and Success responsibilities; these are responsibilities of one presence, not separate agents, personalities, or chat experiences.

### 3.3 Authority separation

The language model interprets questions and selects from approved candidates. It is not the authority for:

- arbitrary URLs or coordinates;
- prices, claims, or commitments;
- sales-stage advancement;
- purchase, checkout, or licensing authorization;
- protected data access;
- governance exceptions;
- arbitrary code execution.

The existing TPC, Correspondence Engine, Doctrine v1, and Nine-of-Clubs sales patterns remain governing architecture where applicable. Their exact interfaces must be validated against the current ORB Weaver repository before implementation.

### 3.4 Commercial authority plane

Commercial truth is governed separately from presentation and cognition.

```text
Approved offer / price / policy / license
        ↓
Vault commercial record
        ↓
Site World intelligence pack
        ↓
Page copy, structured data, ORB answers, checkout preparation
        ↓
Visitor-visible action and evidence
```

TrueMark, Alpha CertSig, licensing, activation, and minting records—where authorized by the Project Brief—remain local-first, deterministic, versioned, and traceable to the Vault commercial record. Page copy, prompts, cached answers, and checkout UI are projections; none is an independent source of truth.

The commercial record must identify its version, effective date, approver, source evidence, allowed presentation contexts, and retirement status. A stale or retired record cannot be selected for a new answer or transaction.

### 3.5 Policy parameters that require explicit ratification

The architecture is universal; these behavior choices are not inferred from it:

- sales posture: restrained, proactive, or Track A / close-oriented;
- funnel stage model and transition evidence;
- whether Weaver remains present on checkout and payment pages;
- allowed proactive initiations and cooldowns;
- default ORB launch/available position;
- aggregate SAFE readiness threshold;
- approved voice interaction model and permission path;
- repository delivery controls;
- reference-site v1 capabilities versus roadmap demonstrations.

Each is recorded in the Project Brief or a versioned global rule. A later site cannot silently inherit a disputed behavior from a prior compilation.

---

## 4. The Site World design model

### 4.1 Information architecture

Every site is both a conventional website and a semantic knowledge environment.

The recommended public structure is:

```text
Home
├── Experience / Demo
├── Solutions / Products
│   ├── Capabilities
│   ├── Use Cases
│   └── Integration Paths
├── How It Works
├── Knowledge / Resources
├── Proof / Case Studies
├── Pricing / Licensing
├── About / Philosophy
└── Contact / Start
```

The site may also include authenticated operator or member areas when the Project Brief authorizes them.

The human-facing hierarchy remains clear and crawlable. The semantic graph adds relationships among pages, products, services, FAQs, articles, proofs, offers, and actions.

### 4.2 The semantic site graph

Traditional navigation is:

```text
Menu → Page → Page → Page
```

Web Weaver adds goal-oriented navigation:

```text
Visitor goal → intent → approved recommendation → verified destination
```

The graph records relationships such as:

- product to capability;
- capability to use case;
- use case to proof;
- proof to offer;
- offer to pricing or licensing;
- question to answer source;
- objection to approved response and evidence;
- support issue to troubleshooting path;
- content node to next learning step.

The graph is a knowledge map, not a replacement for visible page content. Search engines and ordinary visitors must still receive the important information directly.

### 4.3 The knowledge flow

The site should support a progression such as:

```text
Learn → Understand → Evaluate → Implement → Master
```

The ORB may shorten or change that path when the visitor's stated goal requires it. A visitor asking for immediate pricing is not forced through an educational tour. A visitor seeking support is not diverted into sales.

---

## 5. Canonical Project Brief

No page is planned, designed, or built until the Project Brief is complete and approved at Gate A.

The Brief must contain:

1. **Business identity:** name, business function, location, service area, contacts, and approved factual claims.
2. **Owner goals:** what the site must accomplish, in the owner's words.
3. **Visitor groups:** who arrives, what each group is trying to do, accessibility needs, motivations, and likely objections.
4. **Offers:** products, services, packages, policies, and the authoritative source for prices.
5. **Weaver's job:** guide, support, and sales responsibilities; permitted actions; prohibited behavior; escalation rules.
6. **Common objections:** objection text, honest answer, evidence source, and conditions under which the answer may be used.
7. **Brand inputs:** logo, colors, fonts, imagery, tone, required elements, and prohibited elements.
8. **Existing environment:** domains, current pages and URLs to preserve, accounts, services, integrations, and assets.
9. **Content readiness:** owner-supplied content, content to be written, missing material, and approval owner.
10. **Required features:** integrations, forms, voice, analytics, licensing, checkout, booking, or member capabilities.
11. **Operational constraints:** local-first requirements, hosting, permissions, data handling, maintenance, and deployment limits.
12. **Ownership and delivery:** data ownership, access authority, export rights, maintenance authority, and handoff obligations.
13. **Rule acknowledgments:** acceptance of the mandatory footer and signature splash.
14. **Acceptance criteria:** scope, measurable outcomes, approver, approval date, and Brief version.

### Gate A — Brief approval

The named approver signs the Brief. Revisions after approval require a change record and may invalidate page specifications, offers, maps, or tests.

---

## 6. Universal Page Intelligence Specification

Every page receives a human-readable record and a machine-readable specification.

Required fields:

| Area | Required definition |
|---|---|
| Identity | Page ID, route, canonical URL, version, page type |
| Purpose | Why the page exists and what value it provides |
| Objective | What the page must accomplish |
| Intended outcome | Visitor result or action that proves success |
| Audience | Visitor groups, intent, objections, and accessibility considerations |
| Content | Sections, claims, facts, benefits, proof, objections, and sources |
| Visual design | Layout, hierarchy, responsive rules, component states, brand behavior |
| Demo moment | The capability or value the visitor should witness on this page |
| Next sale step | The single most appropriate next step toward an informed decision |
| Search | Search intent, title, description, headings, canonical, internal links, schema |
| Funnel role | Discover, understand, evaluate, decide, act, support, or advocacy |
| ORB knowledge | Answers, explanations, evidence, policies, and citations |
| ORB guidance | Targets, pings, narration, tours, demonstrations, and allowed actions |
| Navigation graph | Related pages, prerequisites, legal transitions, destination state, return path |
| Measurement | Outcome events, verification signals, negative signals, and baselines |
| Acceptance | Functional, visual, responsive, SEO, accessibility, map, governance, and business tests |

A page is complete only when its implementation and specification agree, its page outcome is verified, and its eligible map is complete.

### Page design rule

Every page should communicate one clear value proposition, expose its evidence, provide a real demonstration moment when appropriate, and offer one primary next step. The ORB may reveal alternatives, but it should not create competing calls to action without a visitor-specific reason.

---

## 7. Pointer/Ping Master Map

### 7.1 Target coverage

Map every eligible:

- navigation item and route;
- hero and explanatory section;
- CTA and conversion control;
- pricing, comparison, and proof point;
- FAQ and knowledge resource;
- form field, validation state, and submit control;
- tab, menu, modal, drawer, and accordion;
- demonstration trigger and completion state;
- support resource and escalation control;
- trust indicator, limitation, policy, or relevant disclosure.

Decorative elements do not need to be actionable, but they must not confuse target resolution.

### 7.2 Target record contract

Each target record defines:

- stable identity and page relationship;
- element type and semantic meaning;
- visitor intents served;
- DOM identity and semantic locator;
- validity checks and fallback resolution;
- preferred pointer anchor, offset, clearance, and edge constraints;
- ping location, signal region, duration, and accessible alternative;
- visibility, scroll, menu, modal, form, permission, and prerequisite conditions;
- allowed action and expected destination state;
- priority, safety, interference risk, and authority;
- verification evidence and timestamp;
- failure policy: re-resolve, skip, explain, or offer an alternative.

### 7.3 Geometry policy

Target-relative geometry is authoritative. Permanent hardcoded screen coordinates are not.

Verification must cover:

- desktop and mobile viewports;
- scrolling and sticky elements;
- overlays and dialogs;
- expanded and collapsed states;
- dynamic content and resized layouts;
- disabled, missing, or permission-gated targets;
- keyboard and reduced-motion paths.

If a target cannot be resolved, Weaver must say so or choose a verified alternative. It must never silently advance a tour or demonstration.

### 7.3.1 Independent map, readiness, and outcome measures

These measures are reported separately:

- **Map completeness:** percentage of eligible targets inventoried against the page and state inventory.
- **Target readiness:** percentage of inventoried targets currently `SAFE`, with `UNCERTAIN` and `RECOVERY_REQUIRED` counts.
- **Guidance success:** percentage of attempted guidance tasks whose target and intended destination state were observed.
- **Visitor outcome:** percentage of tasks producing the intended visitor result, such as understanding, support resolution, booking, inquiry, or purchase.

No readiness percentage can excuse an unresolved critical target. A complete map can contain unsafe targets; a safe target can still fail to produce a visitor outcome; and a motion event is not guidance success.

### 7.4 Pointer/Ping lifecycle

```text
Discover → Resolve → Check eligibility → Ping/point → Observe result → Record evidence
```

The map, not random animation, determines the ORB's route.

### 7.5 Ping mechanism specification

Pointer/Ping has three distinct layers:

**Structural map — build time**

- page, route, section, element, semantic role, and funnel tags;
- target relationships and legal destinations;
- expected geometry and state prerequisites.

**Live ping — runtime**

- current route, scroll region, viewport, visible targets, and active state;
- target eligibility and obstruction checks;
- visitor attention signals such as dwell, reversal, hover, focus, or repeated navigation;
- verification of the resulting page or control state.

**Cross-page memory — session scope**

- pages and targets visited in order;
- questions and objections raised;
- unresolved guidance;
- current stage, mode, and completed evidence;
- return path and resumable tour state.

Ping triggers are event-driven, not continuous heavy polling:

- page load or route transition;
- meaningful scroll-threshold crossing;
- CTA, navigation, or comparison hover/focus;
- form focus, validation error, or submission state;
- calibrated idle or hesitation interval;
- explicit visitor request;
- demonstration or tour stop.

The runtime throttles and debounces repeated signals, coalesces events for the same target, and suppresses guidance while the visitor is typing, reading, speaking, using assistive technology, or completing a consequential action. A **passive ping** updates relevance and eligibility without interrupting the visitor. An **active ping** communicates through movement, visual signal, text, or voice only after the target is `SAFE` and the intervention is authorized.

Ping evidence is separate from outcome evidence. A ping can prove that a signal was emitted; it cannot by itself prove that the visitor saw, reached, understood, or completed the intended outcome.

---

## 8. ORB movement and physical design language

The ORB is an autonomous spatial presence, not a chat bubble, cursor accessory, stationary assistant, or decorative animation. Conversation is one capability of the presence; it is never the defining container or primary identity.

### 8.0 Autonomous ORB Presence Doctrine

Weaver is a living-feeling, autonomous digital presence within the website. He moves naturally, observes respectfully, reasons contextually, communicates through natural voice, and helps visitors through verified spatial guidance. His behavior is guided by purpose, courtesy, intelligence, and visitor needs—not by stationary positions, chatbot conventions, or rigid conversational scripts.

The doctrine is absolute:

1. Weaver maintains continuous independent motion. He has no permanent parking position, dock, or stationary resting state.
2. Weaver travels according to environmental awareness, visitor activity, and meaningful opportunities to guide, demonstrate, or assist.
3. A Polite Nudge causes a small natural displacement. Weaver yields without becoming a cursor follower.
4. Weaver respects reading, typing, navigation, personal space, and important screen content. He moves out of the way rather than obstructing the visitor.
5. Natural speech and listening belong to the continuous presence, not to a chatbot interface. Browser-generated voice is prohibited.
6. Weaver exercises contextual judgment and initiative within factual, consent, authorization, safety, and security boundaries. Those boundaries protect the visitor; they do not dictate a rigid personality or every movement.
7. Guiding, demonstrating, supporting, and selling are abilities of one continuous identity, not separate personalities or chatbot modes.

Weaver may become extremely still for a brief, purposeful speaking, listening, pointing, or verification moment. This is temporary courtesy, not docking, parking, or a locked position. Even while yielding space, he remains capable of natural autonomous repositioning.

### 8.1 Visual identity

- The image is the ORB's body.
- Do not place the body inside an unnecessary housing, blue halo, or `local-bloom` wrapper.
- `orb_factory_default_v1` at `/orb-skins/tuxorb.png` is the permanent factory fallback for the reference implementation.
- Custom skins are appearance-only patches. A skin change must not rebuild the Site World, alter the map, or change governance.
- The visual language is precise, calm, direct, and slightly advanced rather than gimmicky.

Skin patches are machine-checkable: the patch manifest may change approved image assets, palette, scale, animation tokens, and presentation metadata only. It may not change page IDs, target IDs, geometry contracts, routes, intelligence sources, commercial records, mode rules, action permissions, policy versions, or evidence schemas. The runtime rejects a skin patch that declares changes outside the appearance schema.

### 8.2 Movement vocabulary

| Movement | Meaning |
|---|---|
| Idle Hover | Low-amplitude presence during inactivity; signals availability without demanding attention |
| Scan Sweep | A restrained sweep and ping used to read or represent the current page map |
| Pointer Ping | A sharp, localized signal toward a verified target |
| Lead / Guide Roll | Purposeful travel to the next relevant section; distance and rotation are coupled |
| Explain Settle | Movement stops, ORB scales slightly, and narration or text begins |
| Taz Transit | Brief rapid transition for long-distance page or section travel; not the default entry animation |
| Recede / Yield | ORB remains in motion while giving visual priority to reading, typing, forms, or a user request; it never locks into a permanent dock |
| Polite Nudge | A small displacement after cursor proximity; never turns the ORB into a cursor follower |
| Yield / Block | Yield clears a control; exit guidance may offer one value-preserving option but never chase a visitor |

The ORB has no permanent screen position. Initial and subsequent placement are resolved from live layout, protected regions, viewport size, visitor activity, and available space. The ORB remains independently ambient and moves continuously at an appropriate low amplitude when not performing a task. It may briefly settle only for a bounded speaking, listening, pointing, or verification moment, then resumes autonomous motion.

### 8.3 Movement arbitration

The controller resolves competing demands in this order:

1. visitor safety, usability, and active-control clearance;
2. authorized guidance and demonstration;
3. speaking/listening posture and readability;
4. ambient movement and personality.

The ORB must not cover active fields, important text, buttons, dialogs, or assistive technology controls. Body motion and eye attention are separate concepts. The ORB does not impersonate the operating-system cursor.

### 8.4 Navigation continuity

The ORB carries identity and appropriate session state between pages. It does not continue a stale instruction after the visitor changes route or state. It reconciles the new page before selecting the next action.

### 8.5 Movement arbitration state machine

Movement is resolved as a state machine rather than a collection of competing animations:

```text
AVAILABLE → GUIDING → SETTLED → VERIFYING → AVAILABLE
     │          │          │
     ├──────→ YIELDING ←───┤
     │          │
     └──────→ INTERRUPTED → RECONCILE
```

Arbitration rules:

1. An active control, text-selection region, dialog, keyboard focus target, or assistive-technology cursor has clearance priority.
2. The controller computes ORB and protected-region bounding boxes in the current viewport. Intersections above the configured clearance margin force `YIELDING`.
3. In `YIELDING`, the ORB moves through the nearest valid perimeter path, reduces amplitude, and pauses nonessential narration. It resumes normal autonomous motion only after the protected region is clear or the visitor explicitly requests continuation.
4. A new visitor action interrupts ambient movement immediately. It interrupts guidance when it changes route, target state, focus, or intent.
5. An authorized demonstration may reserve a target region only for its bounded step; it cannot override active typing, payment, consent, or accessibility controls.
6. After interruption, `RECONCILE` re-reads route, viewport, target eligibility, and Session World before resuming, replacing, or cancelling the task.
7. Every transition records the reason, protected region, selected placement, pause duration, and outcome.

### 8.6 Collision detection contract

Collision checks run against an allowlist of protected regions:

- focused or editable controls;
- submit, payment, consent, and destructive controls;
- dialogs, menus, validation messages, and active media controls;
- readable content currently referenced by narration;
- keyboard focus indicator and assistive-technology interaction regions.

The test records the ORB bounding box, protected-region box, clearance margin, viewport, scroll state, and result. A visual review alone cannot waive a reproducible collision. A collision is a failed guidance condition until the ORB yields or the target is re-resolved.

---

## 9. One ORB, four governed responsibilities

One continuous ORB provides Guide, Support, Demonstration, and Sales responsibilities through the same identity, knowledge, map, permissions, motion system, voice, and Session World. These are governed responsibilities, not separate conversational agents or personalities.

### 9.1 Guide responsibility

**Purpose:** orientation and discovery.

Typical triggers:

- new session;
- first page entry;
- explicit request for help finding something;
- confusion or repeated navigation;
- approved tour request.

Capabilities:

- explain what the page covers;
- answer “where is” questions;
- point and scroll to verified sections;
- offer at most a small number of relevant paths;
- demonstrate spatial intelligence before asking for commitment.

Guide mode does not sell. Its success is verified orientation or destination arrival.

### 9.2 Support responsibility

**Purpose:** resolve friction and route unresolved issues.

Typical triggers:

- explicit support request;
- form error or repeated correction;
- long hesitation on a support or process section;
- repeated question or known-issue signal.

Capabilities:

- diagnose field-level errors;
- retrieve approved answers from documentation and known issues;
- explain policies and limitations;
- guide a safe troubleshooting path;
- offer human handoff with a context summary when unresolved.

If Weaver does not know, it says so immediately and provides the approved escalation route. Unresolved support should reach a human within the exchange count or timing rule authorized by the Project Brief.

### 9.3 Sales Consultant responsibility

**Purpose:** help a visitor make an informed decision and take the correct business action.

Activation requires explicit intent or reliable consideration/decision signals, such as pricing interaction, comparison behavior, repeated product interest, or a checkout/booking action. The reference default does not activate Sales mode merely because a visitor loaded the home page; a more proactive or Track A posture must be explicitly authorized in the Project Brief.

Capabilities:

- identify the visitor's stated need;
- surface one relevant proof point;
- explain approved offers and limitations;
- address common objections with honest, sourced answers;
- summarize fit without inventing certainty;
- guide to a booking, inquiry, purchase, or licensing step;
- request explicit permission before consequential actions.

The ORB does not negotiate pricing, disparage competitors, make commitments, or complete a purchase autonomously.

### 9.4 Responsibility arbitration rule

Weaver chooses the most useful responsibility from current evidence and context; he does not enter rigid scripted personalities. The visitor can request a focus, including “just guide me,” but the continuous presence remains capable of noticing urgent support, accessibility, safety, or task conditions. A support need must not be diverted into sales. A visitor asking for immediate pricing must not be forced through a long tour. The site's approved sales posture may authorize more proactive assistance, but it cannot bypass target, claim, action, or outcome boundaries.

### 9.5 Responsibility arbitration matrix

| Current responsibility | Evidence | Weaver's next responsibility emphasis | Persistence and courtesy |
|---|---|---|---|
| Guide | explicit help request or friction signal | Support | remains until resolution, handoff, or visitor selects another mode |
| Guide | approved consideration or decision evidence | Sales Consultant, if site policy permits | requires a relevant proof point and one next step; declines return to Guide cooldown |
| Support | purchase question after issue is resolved | Guide or Sales Consultant according to stated intent | never transitions while the support issue is unresolved |
| Support | repeated failure or frustration | human handoff | stop automated sales prompts until handoff is accepted or cancelled |
| Sales Consultant | support or troubleshooting request | Support | sales state is preserved but not acted on during support |
| Sales Consultant | visitor asks to browse or learn | Guide | no sales re-entry until new evidence appears |
| Any responsibility | visitor explicitly ends, minimizes, or dismisses ORB | quiet presence | no unsolicited re-entry during the dismissal scope; natural motion may continue only if not prohibited by the dismissal scope |
| Any responsibility | route, focus, or task changes | Reconcile | re-read Session World before continuing |

Explicit visitor intent strongly influences the current task, subject to safety and authorization. Responsibility arbitration is reversible and contextual; it is not a rigid state script. Each emphasis decision records the evidence, policy, confidence, previous emphasis, selected emphasis, and reason for return or cooldown.

---

## 10. Funnel and visitor-intent model

The unified funnel is:

```text
Attract → Discover → Understand → Evaluate → Decide → Act → Support / Expand
```

### Attract

Search, referral, direct, or social entry brings the visitor to a crawlable page. ORB Weaver intelligence improves semantic clarity and discoverability before runtime begins.

### Discover and understand

Weaver establishes relevance, identifies what the page contains, and points to the most useful evidence. It remains restrained during the first moments of a new session.

### Evaluate

The ORB can surface comparisons, use cases, demonstrations, proof, limitations, and approved objection answers. It adapts to research intent, learning intent, support intent, or purchase intent.

### Decide and act

Weaver summarizes the relevant choice and guides the visitor to the correct, verified action. It does not force a universal sequence or click consequential controls without permission.

### Support and expand

After action, Weaver becomes a support and success guide. Approved, privacy-respecting aggregate evidence may improve future Site World proposals, but visitor data does not silently rewrite production truth.

### Intervention rules

- Proactive conversation initiation follows the site policy recorded in the Project Brief and is bounded by relevance, interruption history, dismissal state, and visitor-control rules.
- Every sales-oriented prompt includes a relevant proof element or source.
- If the visitor signals exit, offer one quiet, relevant option; if declined, recede for the session.
- Do not interrupt active reading, typing, forms, checkout, or payment.
- Checkout and payment-page presence follows the approved site policy. When present, Weaver may explain status and guide verified controls, but it may never declare payment complete without authoritative transaction evidence.
- Do not treat ORB activity as usefulness; measure verified outcomes.

### 10.1 Stage Governor input contract

The Stage Governor consumes evidence; it does not treat a single event as decisive. Each signal has a site-configured weight, confidence, decay period, and conflict class. The Project Brief supplies thresholds and whether the site uses the standard funnel or an approved Track A / close-oriented model.

| Signal family | Examples | Typical interpretation |
|---|---|---|
| Entry and discovery | new session, referral, search landing, broad query | Discover / Orient |
| Engagement | section dwell, meaningful scroll, repeated section visit, content completion | Understand / Evaluate |
| Comparison | feature comparison, alternatives question, multiple product paths | Evaluate |
| Commercial | pricing visit, offer question, return visit, booking or checkout initiation | Decide / Act |
| Friction | form correction, validation error, rapid reversal, repeated unanswered question, back navigation from a task | Support / Recovery |
| Explicit declaration | “I need support,” “show pricing,” “book,” “just explain this” | highest-priority task intent |

The governor applies these rules:

1. Explicit visitor intent outranks inferred intent for the active task.
2. Support and accessibility signals outrank sales signals until the issue is resolved or handed off.
3. A stage may advance only when its configured evidence threshold is met and no blocking condition exists.
4. Signals decay after their configured interval; a stale page view cannot permanently force Sales mode.
5. Contradictory signals create a review state or retain the safer mode; they do not authorize a guess.
6. Checkout and payment state may be observed and explained according to policy, but payment completion is proven only by the authoritative transaction system.
7. Every transition records the contributing signals, weights, threshold, policy version, and result.

The following are configurable calibration examples, not universal rules: pricing without action may indicate consideration; pricing plus form or checkout interaction may indicate decision; a return visit within a business-defined window may increase confidence; form failure or repeated reversal may activate support. The values belong in the Project Brief and must be validated against observed outcomes.

### 10.2 Funnel and mode cross-reference

The funnel describes visitor state and desired outcome. Modes describe how Weaver behaves. They are related but not identical:

```text
Discover / Understand → Guide
Evaluate              → Guide or Support
Decide / Act          → Sales Consultant, if authorized
Support / Recovery    → Support
Post-action           → Support or Success Guide
```

A visitor can remain in one funnel stage while changing modes, and a mode change cannot independently advance the funnel.

### 10.3 Contextual initiative doctrine

Weaver's initiative is determined by relevance, not by a universal conversation quota or automatic sales suppression. Before initiating, the ORB evaluates:

- current visitor intent and declared goal;
- target relevance and readiness;
- whether the visitor is reading, typing, speaking, navigating, or completing a consequential action;
- prior interventions, interruption history, and dismissal state;
- available proof and the usefulness of the proposed next step;
- site-specific sales and support policy.

Initiative is permitted when it improves the visitor's current task, demonstrates a relevant capability, resolves observed friction, or advances an authorized business outcome. It is suppressed when it would interrupt, obstruct, repeat a declined offer, expose an unverified claim, or force a stage transition. The same ORB remains present and courteous even when it does not speak.

---

## 11. Demonstration-first design

Every capability claim must have a real demonstration contract.

### Demonstration contract

| Field | Definition |
|---|---|
| Claim | Capability the page says exists |
| Demonstration | What the visitor can witness |
| Required state | Content, route, permissions, and targets that must be ready |
| ORB objective | What Weaver explains or performs |
| Pointer targets | Verified targets supporting the demonstration |
| Expected result | Visible outcome proving the capability |
| Failure behavior | Truthful response if the demonstration cannot proceed |
| Completion evidence | Recorded result, route, target, and timestamp |

The successful result is not that Weaver spoke or moved. It is that the visitor reached, understood, or completed the intended outcome and the system observed that result.

### First-run behavior

Within the orientation window defined by the Project Brief, a new visitor should recognize Weaver as a continuous spatial presence without a tutorial modal:

1. enter through a natural, environment-aware movement;
2. perform a restrained scan or purposeful point toward a verified value or orientation target;
3. remain naturally active without demanding a response;
4. communicate through natural voice when consent and relevance permit;
5. demonstrate spatial guidance on the first meaningful engagement rather than opening a chat window or returning a generic chat answer.

### ORBS Weaver demonstration path

The reference site should demonstrate:

- factory skin and appearance-only skin patching;
- page scan and preflight results;
- Pointer/Ping targets moving from `UNCERTAIN` to `SAFE`;
- navigation to a verified section;
- guide, support, and sales mode transitions;
- approved product answers with sources;
- voice input/output where available;
- an honest failure path when a capability is unavailable.

### 11.1 Failure-honesty UX

Standard visitor-facing failure states are:

| System state | Required response |
|---|---|
| Target `UNCERTAIN` | “I have not verified that destination yet. I can show you the verified alternative.” |
| Target `RECOVERY_REQUIRED` | “That path is unavailable right now. I will not pretend it worked. You can use this alternative or continue without guidance.” |
| Demonstration unavailable | “This demonstration is not ready in the current environment. I can explain the approved capability and show the evidence that is available.” |
| Knowledge unavailable | “I do not have an approved answer for that. I can point you to the source or connect you with the authorized contact.” |
| Action requires permission | “I can prepare this step, but I need your confirmation before continuing.” |
| Voice unavailable | “My approved voice is unavailable right now.” Display only as a non-chat status indication; do not open text chat or offer a text conversation fallback. |

Failure responses must identify what was not verified, avoid fabricated completion language, offer the nearest approved alternative, and record the failure for review. A recovery path may not silently downgrade a blocked target to `SAFE`.

### 11.2 Reference implementation v1 boundary

ORBS Weaver v1 must distinguish capabilities that must work from capabilities that are only shown as roadmap or controlled demonstration.

**Must work:** static and responsive landing page; authoritative footer; approved splash package; Site World load; structural map; target resolution; Guide mode; at least one verified navigation demonstration; approved text answers; accessible controls; truthful failure states; release evidence.

**Requires explicit approval before inclusion:** live payment completion; autonomous checkout; persistent visitor profiles; cross-site deployment; public API; longitudinal personalization; automated content changes; unverified voice fallbacks; any capability that changes licensing, activation, or minting records.

Roadmap capabilities may be shown only with visible status and a demonstration contract that identifies the boundary between simulated explanation and live verified behavior.

---

## 12. SEO and discoverability

Web Weaver serves two readers: search engines and the ORB. The same approved content should support both.

Every indexable page defines:

- search intent and audience question;
- original, accurate, approved content;
- title, description, heading hierarchy, and descriptive URL;
- canonical identity and duplicate handling;
- crawlable rendering and sitemap policy;
- applicable structured data matching visible content;
- descriptive alternative text and optimized media;
- useful internal links derived from verified relationships;
- measured performance, responsiveness, and visual stability;
- local business and service-area facts when applicable;
- approved measurement and consent behavior.

Primary content must be present in the page's crawlable representation. The ORB cannot be the only source of key facts. Progressive disclosure may be used, but critical content must remain available to the indexer and accessible path.

### Rendering strategy

Use server-side, static, or pre-rendered content for core routes where the implementation permits it. Hydrate the ORB intelligence and runtime afterward. The target routes for the reference site include the landing page, major capability pages, and pricing/licensing pages.

### Intelligence feedback

Aggregated, privacy-approved ORB questions and friction patterns may produce editorial proposals:

- recurring questions → FAQ or glossary candidates;
- objections → comparison or alternatives content;
- confusion signals → copy and information-architecture improvements;
- common guidance paths → internal-linking improvements.

These are inputs for review, not automatic publication.

### 12.1 Citation-tracking feedback loop

Every approved ORB answer stores the source page, section, content version, and target relationship it used. The intelligence engine aggregates:

- frequently cited sections;
- questions with no citation;
- answers citing multiple conflicting sources;
- targets reached without a supporting explanation;
- sections repeatedly requested but rarely discovered through ordinary links.

Low-citation or conflict-heavy content becomes a review candidate for copy, internal linking, schema, or page-purpose correction. The loop is:

```text
Question → approved answer → source citation → outcome → coverage/conflict report → editorial proposal
```

Citation tracking improves content and navigation; it does not make the ORB's answer authoritative when the underlying source is unapproved or stale.

---

## 13. Runtime and action boundaries

### 13.1 Allowed action layer

The action layer is allowlisted. It may:

- scroll to a verified target;
- highlight or ping a verified target;
- navigate to a known route;
- open an approved modal, drawer, or section;
- focus or assist a known form field;
- fill known fields only when permitted and confirmed;
- start an approved demonstration;
- prepare a booking, inquiry, or checkout step for visitor confirmation;
- hand off to an approved human channel.

It may not:

- execute arbitrary code;
- click a purchase, payment, submit, or destructive control without explicit authorization;
- alter prices, offers, content, or permissions;
- invent a route or coordinate;
- bypass a governance gate;
- claim a failed action succeeded.

### 13.2 Voice

For the first ORBS Weaver implementation, the approved dedicated speech-synthesis voice is the intended voice. Browser-generated voice is never an approved fallback. Interaction is voice-first and naturally hands-free after explicit microphone consent. A microphone control may exist only as a permission or voice-recovery control; it must not become a chat control or define the interaction architecture. Voice permission, availability, listening, processing, playback, and failure states must be represented truthfully. No text input, transcript, message history, or text-chat fallback may be added to Weaver.

The reference voice path is:

```text
Explicit consent → hands-free listening → approved STT → governed cognition → local LLM path → approved TTS/cache → WAV/audio playback
```

The exact implementation and current repository interfaces must be verified before coding.

### 13.3 Local-first sovereignty

Core site, ORB, licensing, activation, and minting logic remains local-first and deterministic. No paid cloud service or SaaS dependency may be required for the core function unless explicitly approved in the Project Brief.

---

## 14. Accessibility, privacy, and visitor control

Target WCAG 2.2 AA by default, subject to applicable law and approved scope.

Required behavior:

- keyboard and screen-reader access for ordinary website controls and non-conversational ORB controls such as consent, reduced-motion, status, and dismissal;
- visible focus and adequate target size;
- accessible ordinary website content and navigation remain available without converting Weaver into a text interface;
- reduced-motion behavior with no drifting, trails, or unnecessary travel;
- no focus hijacking;
- no obstruction of controls, text, forms, dialogs, or assistive technology;
- explicit microphone, audio, and data permissions;
- session dismissal that is respected for the remainder of the session;
- accessible, non-animated signature splash;
- consent and retention rules defined in the Project Brief;
- no retention of sensitive information merely because the ORB observed it.

The ORB may observe page state required for guidance, but observation is not permission to retain or use information outside the approved purpose.

### 14.1 Dismissal and re-invocation contract

Dismissal is a Session World state, not a cosmetic event. The record contains:

- scope: current task, page, session, or approved longer period;
- timestamp and policy version;
- whether voice, motion, text prompts, or all ORB behavior was dismissed;
- permitted explicit re-invocation path;
- expiration or clearing condition.

An explicit dismissal blocks unsolicited re-entry within its scope. A new session may clear a session-scoped dismissal only if the Project Brief and consent policy allow it. Explicit re-invocation restores only the requested capability; it does not erase previous failure, support, or safety state.

---

## 15. Measurement and learning

### Three evidence layers

| Layer | Example measures |
|---|---|
| Website | traffic source, engagement, page outcomes, performance, SEO, conversion |
| ORB | target resolution, verified guidance, demonstrations, resolved intents, interruptions, failed actions |
| Business | qualified inquiries, bookings, purchases, support resolution, customer confidence, repeat use |

### Core success measures

Use agreed baselines and targets rather than universal claims. Candidate measures include:

- time to first verified ORB value;
- percentage of interactions reaching a relevant destination;
- support resolution without handoff;
- demo completion rate;
- pointer-to-inquiry, booking, or checkout progression;
- pages or knowledge nodes reached through successful guidance;
- form-friction detection before abandonment;
- return-session or deep-link resume rate;
- incorrect guidance, premature sales prompts, obstruction, and unresolved support requests.

### Improvement loop

```text
Observe → Diagnose → Propose → Approve → Implement → Verify → Measure
```

Material changes to layout invalidate geometry. Offer changes invalidate answers. Route changes invalidate the navigation graph. Each change therefore triggers a targeted rescan, re-map, and verification record.

### 15.1 Shared evidence event taxonomy

Website analytics and ORB runtime events use one joinable envelope:

```json
{
  "event_id": "stable-event-id",
  "event_type": "target_verified",
  "occurred_at": "timestamp",
  "site_world_version": "version",
  "session_world_id": "approved-session-id",
  "page_id": "page-id",
  "target_id": "target-id-or-null",
  "mode": "guide|support|sales|none",
  "stage": "configured-stage",
  "policy_version": "version",
  "evidence": {},
  "outcome": "success|failure|interrupted|not_applicable",
  "source": "website|orb|business",
  "privacy_class": "approved-class"
}
```

Minimum event types include `page_viewed`, `target_discovered`, `target_resolved`, `ping_emitted`, `guidance_started`, `guidance_verified`, `guidance_failed`, `mode_changed`, `stage_changed`, `demo_started`, `demo_completed`, `support_resolved`, `handoff_offered`, `handoff_completed`, `offer_presented`, `action_prepared`, `action_confirmed`, `action_completed`, `dismissed`, and `collision_yielded`.

An event does not prove a business outcome unless its evidence field contains the authoritative result. For example, `action_prepared` is not `payment_completed`; payment completion must come from the transaction authority.

---

## 16. Production lifecycle and build sequence

### Gate A — Project Brief

Complete, review, and sign the Brief. No page construction before approval.

### Gate B — Site Intelligence Plan

Inventory the existing environment and define:

- sitemap and information architecture;
- content and source-of-truth plan;
- semantic graph;
- visitor journeys and intent classes;
- offers, objections, and proof;
- SEO plan;
- required integrations;
- map and verification approach;
- acceptance criteria.

Create the Vault structure and reusable foundation. Do not create unfinished public routes merely to satisfy a sitemap.

### Gate C — Landing page

Build the footer first, then the landing page as a complete vertical slice:

1. approved content and visual design;
2. responsive behavior;
3. footer coverage;
4. ORB presence and default behavior;
5. page specification;
6. target discovery and map;
7. guide demonstration;
8. SEO and accessibility checks;
9. business outcome verification.

Accept the landing page before beginning the next page.

### Gate D — Sequential page production

For every subsequent page, repeat the complete page cycle:

```text
Specify → Design → Build → Index → Map → Verify → Accept
```

The page is not done when its route renders. It is done when its content, purpose, outcome, map, interactions, responsive behavior, accessibility, SEO, and governance all agree.

### Gate E — ORB orchestration

After the page set is individually accepted:

- merge Page Intelligence Maps into the Master Map;
- validate the route graph;
- load the intelligence packs;
- configure Guide, Support, and Sales behaviors;
- wire the Stage Governor and action resolver;
- validate cross-page continuity;
- test tours, skip/repeat/change-topic behavior, and human interruption;
- verify approved voice availability, non-chat status, permission, and failure paths.

### Gate F — Full-site acceptance

Run independent:

1. website acceptance;
2. ORB acceptance;
3. business acceptance.

### Gate G — Signature splash

Design and implement the signature opening experience only after the rest of the site is complete. Verify first-time, returning, reduced-motion, keyboard, screen-reader, and footer visibility behavior.

### Gate H — Launch and handoff

Authorize deployment, preserve rollback, verify production from the public path, deliver the release report, and establish maintenance ownership.

The aspirational repeatability benchmark is defined in Appendix B. It applies only after the reusable foundation is verified and must never be treated as a commitment for the first reference implementation.

---

## 17. Release and acceptance standard

### Website acceptance

Verify content, layout, navigation, forms, integrations, responsive behavior, performance, security, accessibility, SEO, footer, and splash.

### ORB acceptance

Verify Site World loading, intelligence sources, target inventory, resolution, pointer/ping geometry, obstacle avoidance, governed actions, approved voice, temporary speech bubble behavior, demonstrations, tours, support, sales boundaries, and failure behavior. Run the FR-09 structural audit; any chat window, chat bubble, chat icon, text input, transcript, message history, text-chat fallback, fixed corner, stationary dock, or browser-generated voice path blocks release.

### Business acceptance

Verify approved purpose, offers, prices, objections, visitor pathways, conversion actions, brand rules, ownership, data handling, and release authorization.

### Release report

Every release report records:

- source revision and build identity;
- page inventory and URL coverage;
- footer and splash coverage;
- Site World, intelligence-pack, and Master Map versions;
- target discovery, resolution, safety, and verification results;
- SEO, performance, security, accessibility, and functional findings;
- demonstration and tour evidence;
- known limitations and approved exceptions;
- deployment verification;
- rollback reference;
- maintenance owner and next review date.

No release claims complete map verification while critical targets remain unresolved or an exception is undocumented.

### 17.1 Contractual traceability

Every major requirement carries a traceability record:

| Field | Required value |
|---|---|
| Requirement ID | Stable identifier such as `FR-02`, `BRIEF-07`, or `PAGE-HOME-OUTCOME` |
| Origin | Blueprint section, originating decision, or approved change record |
| Implementation | Component, data contract, policy, route, or runtime behavior |
| Verification | Automated test, visual check, endpoint result, event evidence, or human acceptance |
| Acceptance criterion | Observable condition for pass/fail |
| Current status | Proposed, implemented, verified, accepted, blocked, or retired |
| Version evidence | Source revision, Site World version, map version, and timestamp |

No requirement is complete because it appears in prose. It must connect to an implementation, verification evidence, and an acceptance criterion. Traceability records are carried into the release report and preserved with the recoverable checkpoint.

Protect the work through one authoritative working project, reproducible checkpoints, protected release references, recoverable backups, and the repository's actual approved delivery workflow. Branches, pull requests, and worktrees are used when they are part of that workflow; they are not created merely to multiply working copies. Do not force-push, rewrite history, overwrite a repository, or use destructive Git commands without explicit approval for that exact command. Every checkpoint identifies source state, Site World version, Master Map version, release evidence, and rollback location.

---

## 18. ORBS Weaver reference implementation

`www.orbsweaver.com` is the first Web Weaver site and the reference environment for validating the production system.

It must:

- explain what a Website ORB is;
- show who it serves and why it is useful;
- demonstrate navigation, Pointer/Ping, support, and consultation;
- answer product questions from approved sources;
- explain offers and licensing accurately;
- provide a legitimate business path for interested owners;
- validate the reusable runtime, skin model, map, motion controller, funnel patterns, and release machinery;
- become the first production evidence for the standard without pretending unverified capabilities are complete.

The landing page is the first accepted public page. The footer is implemented as a shared global component. Every page is mapped as it is built. The signature splash is designed and ratified last on ORBS Weaver, then installed as the versioned standard on later sites.

---

## 19. Final architecture statement

The website is the ORB's structured environment.

The page purpose determines the content. Content determines the semantic and search architecture. Page structure determines the Master Map. The map provides verified guidance candidates. Session evidence determines relevance. Governance determines permissible action. Weaver guides the visitor. Verification determines whether the guidance worked. The resulting evidence informs the next approved improvement.

Web Weaver therefore produces more than pages. It produces a governed, search-visible, human-usable intelligence environment that can function as:

- a website;
- a semantic knowledge graph;
- an intelligent site map;
- a demonstration environment;
- a support center;
- a consultative sales path;
- a customer-success layer; and
- a repeatable local-first website production system.

The required build order is:

```text
Brief → Plan → Landing page → Sequential pages → Map → Ping → Guide → Support → Sell → Prove → Splash → Deliver
```

The operating priority is:

```text
Map → Ping → Guide → Support → Sell
```

The ORB earns the right to guide by being accurate, spatially grounded, visibly useful, and honest about its limits.

---

## Appendix A — Consolidation provenance

The six-response refinement preserves the following source contributions:

| Source contribution | Preserved or refined in |
|---|---|
| ORB as site guide, support agent, and sales consultant | §§1, 9, 10 |
| Structural map, live ping, and cross-page memory | §§3, 7 |
| Vault and single commercial truth | §§3.1, 3.4, 5, 13 |
| Site World / Session World separation | §3.2 |
| Semantic knowledge galaxy and concept relationships | §4 |
| Pointer/Ping lifecycle and SAFE readiness | §7 |
| Movement vocabulary and purposeful physical presence | §8 |
| Funnel behavior and signal-specific intent | §§9, 10 |
| Demonstration-first design | §11 |
| SEO and ORB citation feedback | §12 |
| Action allowlist, voice, and local-first sovereignty | §13 |
| Accessibility, collision, dismissal, and privacy | §14 |
| Evidence layers, event taxonomy, and improvement loop | §15 |
| Gates, page-by-page production, and release evidence | §§16, 17 |
| ORBS Weaver reference scope | §11.2 and §18 |

The table is a maintenance aid, not a ranking of sources. Future changes should update the governing rule, policy version, and affected contracts together.

## Appendix B — Aspirational repeatability benchmark

This benchmark is for a post-foundation, standard-scope site with approved content, a verified reusable runtime, standard integrations, and no exceptional custom development. It is not a promise and does not apply to the first ORBS Weaver implementation.

**Day 1 — Define and build:** approved Brief, Site Intelligence Plan, complete landing page, initial map, and landing-page acceptance.

**Day 2 — Complete:** remaining standard pages, individual maps, integrations, and ORB configuration.

**Day 3 — Prove and deliver:** full audits, corrections, installation of the approved splash package, deployment verification, release report, and handoff.

Any unresolved critical target, commercial-source conflict, accessibility failure, or business acceptance failure overrides the calendar benchmark.

## Appendix C — Final refinement register

| ID | Architectural requirement | Primary implementation location |
|---|---|---|
| FR-01 | Presence before conversation | §§1, 3.2, 8, 9 |
| FR-02 | Purposeful continuous motion; no permanent position, docking, parking, or lock | §§8.0–8.6 |
| FR-03 | Consent-gated, natural, hands-free voice; no browser speech fallback | §13.2 |
| FR-04 | Complete mapping, independent readiness, guidance, and outcome measures | §§3.1, 7.1, 7.3.1, 7.5 |
| FR-05 | One continuous ORB identity across responsibilities | §§3.2, 9, 11 |
| FR-06 | Contextual initiative governed by relevance and dismissal | §§9.5, 10.3, 14.1 |
| FR-07 | Canonical project, checkpoints, protected releases, recovery | §§16, 17 |
| FR-08 | Requirement-to-implementation-to-evidence traceability | §17.1 and this appendix |
| FR-09 | Pure ORB presence and speech-only interface; no chat or text fallback | Rule 13, §§8.0, 13.2, 14 |

These refinements are corrections to the architecture, not a license to remove the Vault, Site/Session World separation, semantic graph, Pointer/Ping map, demonstrations, funnel intelligence, SEO feedback, accessibility, privacy, deterministic action limits, or evidence-based release gates.

