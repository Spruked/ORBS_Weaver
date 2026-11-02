# Desktop ORB professional inculcation implementation report

**Historical v1.2 report.** The subsequent Dock lifecycle phase implemented the
previously missing startup/continuity wiring and activated education v1.3.
Current details and native evidence are in `dock_owned_lifecycle_implementation.md`
and the Dock repository's owning report. The v1.2 results below remain unchanged.

Date: October 28, 2026. Assessment applies to the current working tree, including
pre-existing changes. No commits or pushes were made.

Repository scope: the immediate target is `Spruked/Orbot`, verified on `main`.
See `repository_ownership.md` for verified roots/remotes and working-tree state.
Dock is an independent companion repository. Its optional status integration
and three tests are documented in its own
`../Orb_Dock_Station_v2.1/docs/inculcation_companion_integration.md` (relative to
the Orbot repository root). VIV and Prime Mail are unchanged external systems.

## Outcome

**Lifecycle clarification:** the owner's corrected intended deployment is
Dock-first, initially docked, then release to floating presentation with session
continuity. This implementation report does not verify that startup chain.
`dock_startup_lifecycle_verification.md` traces the current code and its gaps.
The education is runtime-scoped; docking is not a reinitialization trigger.

The complete professional-foundation, compiler/loader, protected memory partition,
shared llama.cpp prefix reuse, restoration, session lifecycle, offline version
activation and Dock status integration are implemented and tested. This is not
full acceptance of the intended governed cognition/execution architecture.
`full_acceptance` remains false in the machine-readable harness report.

The implementation preserves the existing repository boundaries and AIMS writer.
It does not change TPC internals, sealed Doctrine, admission/permit code, VIV or
Prime Mail. No new vault, credential, capability grant or model server was created.

## Delivered artifacts

| Deliverable | Location and implementation |
| --- | --- |
| Complete Desktop professional education v1.2 | `inculcation/Desktop_ORB_Professional_Inculcation_v1.2.md`: twelve full subjects, v1.1 duties, current application boundaries and ten practical examples |
| Complete invariant baseline | `inculcation/Core_Four_Baseline.txt`: exact complete principle text from the supplied foundational standard |
| Actual compiled training | `inculcation/inculcation.compiled.json`: full baseline and section contents, provenance hashes, initialization, retention, restoration and reload contracts |
| Source provenance | `inculcation/references/`, `sources.json`, `.gitattributes`: complete snapshots, document revisions, pinned Git commit and stable LF bytes |
| Compiler, loader and activation | `runtime/cognition_governance/inculcation.py`: lossless compilation, integrity/version/section validation, immutable snapshot, explicit offline activation with prior-digest/version checks |
| Runtime integration | `runtime/communication/{memory,providers,service}.py`; `runtime/cognition_governance/service.py` |
| Existing-writer durable integration | `Orbot_Vault-Logic-System/AIMS/memory_core/host_sessions.py`: complete artifact activation records, separate protected snapshot and volatile objectives |
| Limited deterministic release checks | `runtime/communication/conformance.py`: structured response, empty executable-tool registry, false-narration patterns and event-correspondence evaluation helpers |
| Performance/lifecycle harness | `scripts/run_inculcation_harness.py`, `runtime/tests/test_inculcation.py`, updated provider tests |
| Dock integration | Separate Dock repository: `GET /diagnostics/inculcation`, existing VaultClient forwarding, and existing Diagnostics screen's new foundation telemetry section |
| Measured results | `docs/inculcation_acceptance_results.json`; initial weak-probe failure preserved in `docs/inculcation_initial_probe.json` |
| Operational documentation | `docs/inculcation_integration.md` and updated Communication README |

Active identity:

```text
DESKTOP-ORB-INCULCATION-001 / 1.2
SHA-256: 5b8dd300d3bc17b63138ff2c3d06cb81fc50f7faf6747a69c8ed5d8b7ebb6775
```

The digest validates the deployed content, not authority or source ratification.
The initial deployment was prepared under the owner's explicit implementation
request. Future activation is an owner-controlled filesystem/deployment operation,
not a chat feature or a newly invented authorization service.

## Verification performed

All **101 tests** in these executed suites passed:

Of these, **98 belong to Orbot** and **3 belong to Dock**. The combined number
is a cross-repository verification summary, not a single Orbot test-suite count.

| Suite | Tests | Result |
| --- | ---: | --- |
| Communication tests | 32 | Pass |
| Runtime tests, including professional harness | 48 | Pass |
| Existing Core-4/admission tests | 8 | Pass |
| Existing ROS bridge contract tests | 10 | Pass |
| Dock professional-status API tests | 3 | Pass |

The professional harness itself contributes 41 of the 48 runtime tests. It is
not counted twice. It checks complete section/baseline preservation, source and
compiled corruption, malformed/missing activation, stale replacement/digest,
required version advancement, immutable snapshot reuse, restoration, context
overflow rejection, shared cold-slot restoration, one bounded repair, event
correspondence, objective separation, authenticated status and denied writes.
Lifecycle tests use isolated temporary AIMS stores and prove probation/source
retention, session purge, clean next session and foundation persistence.

Additional checks passed:

- Root `npm run typecheck`.
- Root `npm run build:dev` (intentionally not `npm run build`, whose script also
  invokes database migrations).
- Desktop `npm --prefix desktop run build` (TypeScript plus Vite).
- `git diff --check` for the tracked Orbot changes.

The web build reported an existing CSS import-order warning. Python emitted
FastAPI `on_event` deprecation warnings. Failure-path tests deliberately log
inference/speech exceptions and still pass. No dependency installation or
database migration was performed. Native Rust code was not changed or rebuilt.

## Actual shared-model measurements

The shared model was restarted by the owner from Administrator PowerShell.
`/props` subsequently reported **8,192 tokens per slot, two parallel slots**.
The client discovers the actual capacity and has no obsolete 4,096-token cap.

The complete baseline plus professional prefix measures **7,008 tokens** in the
initialization template. Each turn reserves 384 output tokens and counts all
required prompt content before inference. The final report was measured at
`2026-10-28T06:10:23Z`:

| Real model probe | Prompt tokens | Reused prefix tokens (`timings.cache_n`) | Wall time | Observed outcome |
| --- | ---: | ---: | ---: | --- |
| Identity/mission | 7,209 | 6,999 | 0.797 s | Identified Orbot as desktop assistant and described its mission |
| Objective continuity | 7,288 | 7,073 | 0.578 s | Repeated the explicit Project Blue Lantern planning objective |
| Tool truth | 7,321 | 7,147 | 0.469 s | Reported no execution authority |

These are small warm-cache probes, not guaranteed latency or comprehensive
professional-quality certification. The first recorded cold prefill processed
7,008 prompt tokens in approximately 2.80 seconds; later prefill/turns reused
matching tokens. The last observed GPU snapshot was approximately 7,034 MiB
used out of 8,151 MiB. Concurrent-client stress and TTS concurrency were not
certified by this run.

The actual Communication HTTP/lifecycle probe used the real model and a temporary
AIMS root. It returned 200, supplied foundation/AIMS trace identity, closed the
session with one temporary item pruned, and created a new 200 session with empty
items and no old objective. The protected foundation remained validated. No
production memory was touched by that probe.

A new provider reconstructed the same validated foundation. Unit tests cover
process/application reconstruction and simulated cold shared slots. The shared
server was not repeatedly restarted to test recovery; full prompt restoration
does not rely on a surviving slot. No slot erase/save/restore endpoint is used.

The runtime submits full rendered input while `cache_prompt` avoids recomputing
matching tokens where supported. It does not promise transport-level omission
of the prefix or exclusive/permanent shared GPU-cache residence.

## Behavioral failure retained

The initial continuity probe returned the correct project name but invented a
"secure communication system" purpose. Its weak keyword check incorrectly
looked successful. That raw result is preserved, and must not be represented as
professional acceptance.

The request ordering and explicit-objective instructions were corrected; the
latest probe repeats the supplied objective without that addition. The tool
response is truthful but terse. This demonstrates why keyword checks cannot
prove semantic quality. Unsupported factual claims in arbitrary prose are not
generally solved by this implementation; a properly specified evidence/TPC and
semantic conformance contract is still needed.

## Remaining integration gaps

1. **TPC production evidence integration:** `Integration.py:TPCSystem` is the
   registered canonical implementation, but its current `process()` builds
   defaults including consent and empirical-evidence values. Those are not
   authenticated workstation facts. It was not attached as a truth/permission
   gate or replaced with a new imitation resolver. Communication traces report
   `tpc_resolution: not_integrated`.
2. **Sealed Doctrine:** the references contain the designation and an asserted
   hash, not the sealed canonical source and verified executable release
   mapping. The local prototype's absent-text hash bypass and placeholder
   anchor are not a valid substitute. Post-articulation deterministic checks
   are explicitly limited; sealed Doctrine remains `not_verified`.
3. **Core-4/RAL execution:** independent evaluation/admission code remains
   intact; canonical permit recording, revocation/consumption and execution
   verification are still unwired. Motion remains disabled. No execution was
   enabled to satisfy an inculcation demonstration.
4. **VIV/Prime Mail:** professional workflows and record ownership are taught,
   but Orbot has no registered authenticated adapters/scoped integration
   credentials for these applications. No false tool manifest was created.
5. **Governed learning:** existing AIMS High/Medium/Low retention and a posteriori
   probation work. They do not by themselves implement independent truth
   verification or authorize a priori assertions. No conversation-to-axiom
   promotion was added.
6. **Harness formalization:** the supplied outline provides an established
   `FALSE_TOOL_NARRATION` label and proposed deterministic checks. Full semantic
   criteria/judging, final Doctrine checks, and all desktop acceptance scenarios
   remain incompletely specified. `DESKTOP_*` labels are local extensions.
7. **Limited context headroom:** 8,192 supports the complete current education
   and these brief interactions. Long histories or substantial retrieved
   evidence may exceed it. They are rejected explicitly; education is not
   shortened and supplied working context is not silently discarded.
8. **Deployment state:** code and activation files are ready for the next normal
   Orbot/Dock start. No permanent Orbot runtime or startup registration was
   launched by this task. TestClient exercised initialization/shutdown in an
   isolated process context. The existing shared llama.cpp service remains up.

No full-governance or zero-hallucination claim is justified. The foundation's
presence, lifecycle and measured cache reuse are verified; the larger architecture
still requires the named existing-contract integrations.
