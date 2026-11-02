# ORBOT Dock Station Diagnostics specification

Status: implementation specification, not a claim of implemented capabilities.

The separate Dock Station is the operator's inspection surface for ORBOT's
Communication, Cognition/Governance, Motion, and AIMS foundation. Diagnostics
must explain what was perceived, proposed, authorized, executed, and independently
verified. ORBOT remains operationally independent of the Dock Station.

## Measurement contract

Every displayed value must carry its measurement time and producer/source.
Use UTC timestamps in transport and show the operator's local time in the UI.
Distinguish measurement time from collection/receipt time. Show age and freshness;
an old successful measurement must not appear as current health.

Unmeasured values display **unknown**, never fabricated zero, false, healthy,
passed, armed, or an empty list implying a measured absence. A failed poll means
reachability is unknown/unavailable; it does not prove a process stopped. Show
running/stopped only when process or lifecycle evidence supports that claim.
Preserve the last measurement separately when the producer disconnects.

Use a common envelope for each metric:

```json
{
  "metric": "motion.enabled",
  "value": null,
  "status": "unknown",
  "measured_at": null,
  "received_at": "2026-10-20T00:00:00Z",
  "source": "motion",
  "process_instance_id": null,
  "reason": "No measurement received"
}
```

`status` distinguishes measured, unknown, stale, and error. Staleness thresholds
must be documented per metric. Null is not numeric zero. Configuration declarations
must be labeled configured/saved, distinct from measured runtime state. Readiness
requires individual schema, policy, grant, and adapter validation results; process
presence and a responding health route do not establish these validations.

## Required measurements

| Area | Required values |
| --- | --- |
| Runtime health | Running/stopped for Communication, Cognition/Governance, Motion, Vault/AIMS, llama.cpp, Dock backend; uptime; last restart; startup validation results for schemas, policy, grants, adapters; heartbeat age; bound ports and conflicts; errors and crashes over the last hour and day |
| Hardware/resources | GPU used/free memory, utilization, temperature; GPU-resident models and attributable memory per model; CPU/RAM per runtime; free/total disk space for Vault, AIMS, model folders |
| Intelligence/models | Active model, provider, local/remote mode; response latency; tokens/sec; failed/timed-out calls; clearly visible remote-provider enabled state and whether a call used a remote destination |
| Speech/hearing | Microphone active/muted/unavailable; idle/listening/processing state; Cochlear status and distortion enabled state; recent recognition confidence; heard/corrected/confirmed counts; clarification count; stop-word path armed state, last trigger and latency; TTS loaded model, selected voice, sentence generation duration; end-of-speech to playback-start latency |
| AIMS memory | Current session ID and STM size; session LTM promotions with reasons; totals by collection; last Vault integrity check/time/result; single-writer process identity and lock ownership evidence; rejected/failed writes; SKG node/link counts and last update; index rebuild state |
| Cognition/governance | RAL idle/evaluating/waiting/deferred state; active goal; recent proposals with separate Kant/Locke/Hume/Spinoza results; admitted/rejected/deferred decisions and reasons; Epistemic Gravity Field readings and random seed per run; World State version and age |
| Authority/permits | Active grants with scope/expiry; issued/active/expired/revoked/consumed permits; rejection reasons including expired, altered, duplicate, invented, stale; revocations |
| Execution/Motion | Motion enabled/disabled and reason; queue depth for motion/pointer/speech/tool lanes; active/cancelled actions; cancellation latency; emergency-stop armed state, last test/result; watchdog state |
| Correspondence | Actions awaiting verification; verified/contradicted/unknown/partial outcomes; reported-success versus unobserved-effect discrepancies |
| Orb/dock | Docked/undocked, visible/hidden; Orb position/current behavior; active skin; settings saved versus acknowledged as applied live |
| Security | Per-route authentication required state and mechanism; rejected requests with source; failed logins; doctrine/policy hash check result/time |
| Activity log | Live correlated timeline of perception, interpretation, proposal, decision, authorization, execution, observation, verification |

## Accountability and provenance

Each cycle gets a stable cycle ID. Events also have unique event IDs, causation
and correlation IDs, producer/process instance, occurrence/receipt timestamps,
schema version, and references to supporting records. Preserve proposal, permit,
execution, receipt, observation, and correspondence identifiers where applicable.
Do not collapse concurrent events into a falsely ordered global sequence.

Keep original audio reference, raw recognized transcript, perceptual interpretation,
correction hypothesis, and confirmed meaning distinguishable. Intentional Cochlear
distortion remains part of perception. A guessed correction cannot overwrite the
original input, count as user confirmation, or establish execution authority.
Audio retention follows AIMS policy; diagnostics must not create a private audio
or transcript store. Show unavailable provenance explicitly.

Discussion, intent, permission, execution, and independently verified success are
separate event types. A successful HTTP response, worker receipt, model statement,
or simulation does not establish a verified effect. Field coherence/confidence
does not establish truth or permission. Core-4 evaluation and hard admission stay
deterministic and independent of model output alone.

Counts require a stated time window and observation coverage. A counter reset
or process restart must not silently produce a complete-looking hour/day count.
Use monotonic clocks for durations and wall-clock UTC for event timestamps.
Report token throughput only when token counts and elapsed time are measured.
GPU process memory is not per-model attribution unless that attribution is known.

Record the field's actual seed before initialization and identify the process/run
and relevant RNGs. Do not invent a seed for an already initialized stochastic run.
A seed by itself is not a guarantee of reproducibility across software/devices.

## Ownership and access

Producers measure their own state. The diagnostics aggregator reads their scoped
telemetry and OS/resource observations, preserving source timestamps. The Dock
renders this evidence; it cannot issue permits, alter policy, promote memory truth,
or start execution through a diagnostics read operation.

AIMS remains the sole durable truth/write authority. Writer telemetry must expose
actual lock ownership and detect zero/multiple owners; a singleton Python object
alone is not proof of a cross-process single-writer lock. Telemetry persistence
uses the canonical authority path with bounded retention and redaction. Never
record credentials, bearer tokens, secrets, or unrestricted sensitive payloads.
Access to detailed hearing/activity data follows authenticated operator scope.

## Current implementation gaps

Existing health/status routes, memory inspection, native docking state, local model
queries, and field diagnostics provide partial inputs. They do not yet satisfy this
measurement contract. Current `ready: true` values do not prove policy/grant/schema
validation. Existing fixed health fields and empty placeholder reports must become
unknown until measured. Motion commands are disabled; this is not proof that an
emergency stop or watchdog is armed.

RAL scheduling, canonical permit issuance, governed execution, independent
correspondence, confirmed hearing feedback, full audio provenance, field seed
capture, and complete per-cycle tracing are incomplete. Dock configuration storage
does not establish live application. Do not enable simulated legacy test routes
as a substitute for real telemetry.

## Acceptance criteria

1. Every displayed metric exposes source, measurement time, age, and freshness.
   Missing measurements render unknown; measured zero remains distinguishable.
2. Disconnects, restarts, timeouts, stale data, port conflicts, and unavailable GPU
   telemetry render accurately without inventing healthy/stopped states.
3. Each service exposes individual startup-validation evidence. Error/crash counts
   disclose retention windows, coverage, and restart discontinuities.
4. Voice traces preserve perception versus hypotheses versus confirmed feedback.
   Latency measurements use actual capture/playback events, not server completion.
5. Memory diagnostics identify the measured writer/lock owner, integrity results,
   retention reasons, write failures, and derived-index state.
6. An operator can follow one cycle through separate Core-4 results, admission,
   grant/permit evidence, execution, and independent verification. Missing stages
   remain explicit. Rejections retain reasons without executing rejected work.
7. Field diagnostics report actual run/seed provenance; unsupported attribution
   or historical seed information remains unknown.
8. Saved settings and runtime-applied settings are visibly distinct and versioned;
   only producer acknowledgement with time establishes application.
9. Diagnostics reads have no execution side effects. Authentication tests and
   redaction checks cover protected data, failed requests, and event streams.
10. Simulated tests cannot populate measured-success or verified-effect displays.

Implementation order: establish the common metric/event contract and remove
fabricated defaults; add runtime/resource telemetry; add voice/memory provenance;
then connect governance, permits, execution, and correspondence as those real
capabilities become available. Display all required areas throughout, marking
missing measurements unknown.
