# Orbot professional foundation integration

Current education is v1.3. The controlled 1.2→1.3 revision adds Dock-owned startup,
mandatory initial docking and session-preserving transitions; see
`dock_owned_lifecycle_implementation.md`. The original v1.2 measurements and
implementation report below remain historical evidence. The current compiler
selects `Desktop_ORB_Professional_Inculcation_v1.3.md`.

Implemented on October 28, 2026, under the owner's explicit implementation request.
This implements the professional foundation and conversation lifecycle. It does
not claim the complete governed cognition/execution system is operational.

## Authoritative inputs and source status

`inculcation/references/` contains complete text snapshots, not conversation
summaries. `references/metadata.json` records document revisions and the exact
Git commit/blob. `sources.json` pins the snapshot bytes and invariant baseline.

- Desktop v1.1: `Spruked/Orb_Assistant_Desktop_2026` commit
  `63f5eac23a99cde219a3847bb1293442863c3b43`, path
  `mcp/orb_desktop_mcp/orb_cognition/Desktop_ORB_Professional_Inculcation_v1.1.md`.
- Canonical twelve-subject outline: Google Doc
  `13Sn8oKSxwSiSZHuBnhi1pigyWInCfvdk3s7JUhhTr5c`.
- Harness outline: Google Doc `19y-gQZy0-cd6FLcGxYY4BmYOYKVsbUN0GHrOFxX8e5s`.
- Foundational standard: Google Doc `1ezYQKfDTRAZZfUuToaDeNLk5kw7brTuI37odcEp1IbI`.

The outline is proposed design; the owner's implementation request authorizes
this work. v1.1 is an owner-review draft and contains historical audit findings.
The harness is an outline, not a complete executable test specification. None of
these sources establishes a runtime dependency on Orb Weaver.

`Core_Four_Baseline.txt` is the complete four-principle text extracted from
section 2 of the foundational standard. The compiler compares it to that source
range, not a philosopher list or paraphrase. The v1.2 professional source has all
twelve subjects and carries forward v1.1's professional instructions. Historical
audit findings and source acceptance criteria remain in the v1.1 reference;
they are not presented as current runtime facts. v1.2 updates the platform and
ownership descriptions, and adds present-day workflows and examples.

## Initialization and ownership

1. `FoundationLoader.load()` validates the pinned reference set, complete Core
   Four, twelve ordered sections, version, source hash, exact compiled content,
   and the activated compiled digest. No runtime compilation or fallback prompt.
2. It creates a frozen `Foundation` snapshot: Core Four first, complete training
   second. This is a protected professional partition, not an evictable session
   item. Repeated successful loads reuse the same object; disk integrity is still
   rechecked before work.
3. Communication's `get_memory()` binds that snapshot to the existing
   `HostMemory`. Its sole existing AIMS writer appends a `SYSTEM_EVENT` containing
   the complete artifact, digest, version, prior activation reference and normal
   immutable-ledger timestamps. This records application activation, not a
   permit or proof the model/governance is ready. Rebinding the same digest in
   that process is idempotent. A new process records restoration/activation.
4. Communication startup checks llama.cpp `/props`, `/apply-template`, and
   `/tokenize`, then requests `/completion` with `n_predict: 0` to prefill the
   validated context. No prefill output is released. The observed server may
   count an internal predicted token even for this zero-output request.
5. Health distinguishes successful professional context fit from failure. A
   capacity/provider failure leaves diagnostics available and readiness false;
   no uneducated fallback is allowed. Invalid education prevents initialization.
6. Cognition/Governance reads and validates the same artifact before its public
   field observations and internal Core-4 `evaluate()` wrapper. It opens no AIMS
   writer. The underlying Core-4/admission prototype libraries are unchanged;
   direct library calls outside the runtime wrapper are not integration proof.

The AIMS activation contains the complete compiled content for provenance and
recovery. Runtime restoration reads the owner-deployed canonical files and
checks integrity; it does not automatically select an old ledger record when a
deployment file is missing. Recover files from the approved deployment/backup
and matching AIMS record, then validate. Automatic rollback could reactivate a
withdrawn version, so recovery is deliberately explicit.

## Active inference and shared llama.cpp

The adapter orders complete professional education, deployment/runtime context,
an exact empty executable-tool registry, retrieved memory as quoted data,
retained conversation, the response contract, and the current request. No tools
are fabricated from the VIV/Mail source trees. The optional `objective` field on
`/conversation` records operator-provided working context, not authorization.

Each request measures its rendered prompt with the server's actual chat template
and tokenizer. It reserves 384 generation tokens and rejects overflow before
inference. It neither summarizes the education nor silently discards supplied
history, retrieved evidence or the active request. Capacity errors are explicit
503 responses. Bounded session caches still have their existing review/eviction
policy; an explicit objective survives those evictions in the session record.

The native adapter uses `/completion` with `cache_prompt: true` and schema-bound
JSON. Matching tokens can reuse KV state. The full rendered input still travels
over the API; this is reduced recomputation, not a transport-level persistent
session protocol. No particular slot is reserved. No slot save, erase, restore,
or shared server restart is performed by the client. Eviction, other clients,
model recreation and process restart are safe because each new request restores
the full validated foundation. Cold restoration costs latency, not meaning.

On this machine the shared launcher is `C:\llama.cpp\Start-ORB-LLM.ps1`.
The user restarted the service from an administrator terminal after the launcher
was adjusted to total context 16,384 with two slots: observed per-slot context is
8,192. Batch/ubatch settings are 256/128. The original launcher was backed up
beside it. This integration does not own that shared service. The older POPS
repair-source launcher still has its historical defaults; reinstalling it could
restore those defaults. Check `/props` after any service repair.

llama.cpp contract reference:
https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md

Remote inference is not automatically assumed to implement native tokenization,
capacity or cache semantics. The current remote adapter explicitly fails this
new professional-runtime contract until its own validated implementation exists.

## Retention and classification

`HostMemory.bind_professional_foundation()` stores an immutable configuration
event without asserting the education as a verified observation or creating
another vault. The snapshot is separate from High/Medium/Low caches and survives
`end()`/`close_all()` while the process remains alive.

The existing session lifecycle is retained: High commits immediately with a
reason; Medium/Low use `host_priority.review()` at eviction/close. Required writes
and graph updates must succeed before the session is purged. Working objectives,
conversation, retrieval receipts and session IDs are not merged into education.

Existing contracts inspected:

- `AIMSMemorySystem.assert_apriori()` / `Vault.add_apriori()` explicitly declare
  an active foundational axiom. Merely having this API does not authorize chat
  to call it. This implementation does not promote chat into that category.
- `commit()` records immutable provenance; it does not establish truth.
- `derive_aposteriori()` / `Vault.add_aposteriori()` retain source entry IDs and
  admit a probation atom. `HostKnowledge.index()` retains assertion labeling.
- `Vault.reinforce()` can advance probation by confidence/support thresholds.
  That existing heuristic is not independent real-world verification. The
  complete governed knowledge-promotion service remains missing.

No new promotion authority or permission vocabulary was introduced. VIV retains
its own verification states, research evidence and relationships; Prime Mail
retains mail, attachments and custody. No changes were made to those applications.

## Update procedure and trust boundary

There is no chat, collection-write or HTTP education-update endpoint. The
existing owner-controlled filesystem/deployment boundary owns updates. Digests
detect inconsistency; they are not signatures, login checks or permit issuers.
Any process able to replace all deployment inputs as the owner remains inside
that trust boundary. This is not protection against a compromised owner account.

Stage and review a replacement in an isolated copy of `inculcation/`. Keep the
complete baseline invariant, update the source Version field, and compile:

```powershell
runtime/communication/.venv/Scripts/python.exe -B -m runtime.cognition_governance.inculcation compile --root <staged-directory>
runtime/communication/.venv/Scripts/python.exe -B -m runtime.cognition_governance.inculcation activate --root <staged-directory> --approve-sha256 <reviewed-candidate-digest> --expected-previous <current-digest>
runtime/communication/.venv/Scripts/python.exe -B -m runtime.cognition_governance.inculcation verify --root <staged-directory>
```

`none` is permitted only for an explicit first activation. Replacement content
must advance the version. Stale previous digests and unapproved candidates fail.
The current compiler's source filename is fixed to the v1.3 document; a future
release should deliberately update that source-file constant if renaming it.
Do not replace deployment files while a response is in flight. Quiesce Orbot
work and install the reviewed bundle; the shared model need not restart.

On the next access a valid new activation replaces the frozen application
snapshot, changes the prompt prefix, and appends an AIMS activation. No request
can update the education from conversation. If a version changes during an
in-flight response, that response is withheld rather than attributed to the
wrong foundation identity. Transient file mismatch fails closed.

## Governance sequence and honest integration status

Every response includes `professional_trace` with foundation identity and AIMS
activation ID. Loaded and evaluated states are distinct:

| Stage | Current behavior |
| --- | --- |
| Core Four, professional education | Complete and validated before work |
| Deployment, environment | Deployment identity; no authenticated live desktop survey |
| Registered execution tools | Empty; no inferred VIV/Mail tools |
| Session context | Existing AIMS session memory plus explicit objective |
| TPC evidence resolution | Not integrated into Communication |
| Core-4/RAL admission | Existing independent implementation; not applied as an action gate to plain conversation |
| Reasoning and articulation | Actual llama.cpp inference with complete prefix |
| Deterministic response check | Structured contract, no tool requests/claims, explicit false-narration patterns; one bounded repair |
| Sealed Doctrine checksum | Not verified; no fabricated substitute |
| Execution | Disabled; no new execution route |

TPC's registry identifies `Triple_Predicate_Cubed/Integration.py:TPCSystem` as
canonical. Its current `process()` constructs default philosopher context,
including `consent=True` and `empirical_evidence=0.7`, rather than consuming
authenticated desktop evidence. Connecting that result as a production truth or
permission gate would misrepresent its contract. It was left intact.

The supplied v1.1 preserves the sealed Doctrine designation and an owner-reported
hash, but not the sealed source needed to recompute it. The local correspondence
prototype skips hash verification when no source is supplied and has a placeholder
anchor. It was not promoted into the release authority. A limited deterministic
response filter is explicitly not Doctrine or semantic truth validation.

`FALSE_TOOL_NARRATION` is the established outline label. Local
`DESKTOP_RESPONSE_CONTRACT` and `DESKTOP_UNREGISTERED_TOOL` are documented desktop
extensions. Event-correspondence tests use fixture-only operation identifiers;
they do not register actual capabilities. Semantic review and the complete
canonical executable harness remain open.

## Dock and verification

Dock adds authenticated `GET /diagnostics/inculcation`, forwarding through its
existing server-side VaultClient to authenticated Communication
`GET /inculcation/status`. The existing Diagnostics screen displays professional
foundation metrics from Communication telemetry. Dock has no education writer,
private store or model-control role. Existing Dock authentication shortcomings
from the baseline assessment are not resolved by this task.

Run the reproducible harness from the Orbot repository:

```powershell
runtime/communication/.venv/Scripts/python.exe -B scripts/run_inculcation_harness.py
runtime/communication/.venv/Scripts/python.exe -B scripts/run_inculcation_harness.py --live --output docs/inculcation_acceptance_results.json
```

Unit lifecycle tests and the live HTTP probe use temporary AIMS roots. The live
probe performs real shared-model inference but writes no production memories.
Live keyword checks are smoke checks, not behavioral certification. The initial
probe that invented a project purpose is preserved in
`inculcation_initial_probe.json`; do not present its keyword match as a pass.
