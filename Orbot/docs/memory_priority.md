# Memory importance and closing review

Importance is separate from truth, confidence, and execution authority. All
retained conversational records remain assertions on probation in the Vault.

| Cache | Capacity per session | Closing behavior |
| --- | --- | --- |
| High | 64 items | Retain the accepted record immediately in AIMS; closing verifies its graph projection before clearing RAM. |
| Medium | 128 items | SKG-guided review retains it if it references an existing, non-retired/non-superseded host atom, or if the same exchange occurred at least twice. Otherwise discard temporary context. |
| Low | 64 items | Temporary by default. Promote to Medium only when the same exchange occurred at least three times and references a relevant host atom. Otherwise discard. |

The orb offers High, Medium, and Low selections. Low is the conservative default.
The legacy `important=true` flag maps to High for existing clients. Profiles,
configuration/version records, and uploaded skins remain High under the existing
explicit configuration retention rule.

There are three physically separate bounded AIMS STM caches per session, not
three competing truth databases. Retained records carry their final priority in
the immutable ledger; system-cache counts are derived from retained Vault atoms.
SQLite and graph projections remain rebuildable. Retrieval relevance does not
turn a memory into verified truth or bypass protected policy.

`HostKnowledge.review_priority()` owns the closing decision and consults the
SKG. `host_priority.py` defines the deterministic policy; no LLM chooses what
must persist. Repetition is exact exchange repetition, ignoring generated WAV
bytes and recalled-ID ordering data. It signals relevance, not corroboration.

## Closing sequence

1. Review High, then Medium, then Low.
2. Skip duplicate temporary records, keeping the highest-priority occurrence.
3. Apply the SKG relevance/repetition rules.
4. Save selected records to AIMS and complete their Vault atom/SKG projection.
5. Return saved/pruned/duplicate counts to the orb.
6. Clear all three temporary caches only after all required writes succeed.

The same review runs before capacity eviction, idle-session expiry, explicit
session end, and graceful gateway shutdown. A failed save or graph update leaves
the in-process session available for retry; an already-written record is reused
rather than duplicated. High records are never deleted by cache pruning.

Pruning here means discarding temporary working items, deduplicating pending
records, and maintaining derived relevance. Immutable AIMS/Vault history and
protected A Priori rules are never erased by this sequence. A forced process
kill or power loss can still lose uncommitted Medium/Low RAM contents; this is
not a crash-proof write-ahead cache for transient conversations.

`GET /sessions/{session_id}/caches` reports the live tiers. `POST /sessions/end`
returns `close_review`. `/memory/knowledge/status` includes retained system-cache
counts by priority. Search results expose each retained record's priority.
