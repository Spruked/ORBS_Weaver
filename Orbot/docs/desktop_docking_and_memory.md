> Voice lifecycle update: docking now preserves active microphone and playback; only explicit Pause/Cancel or shutdown suspends media. Earlier suspension descriptions below are historical. See voice_pipeline_status.md.

# Native embodiment, separate station, and AIMS memory

## Corrected intended launch lifecycle

Dock Station is Orbot's primary launch and activation environment. Orbot must
launch through Dock, start docked, and be released into its floating Tauri
presentation while retaining the same cognition, identity, memory and active
session. Docking/undocking must not reinitialize inculcation or end the session.
Independent repositories/processes remain; independent manual launch is not the
intended deployment. Historical separate/manual-launch instructions are
superseded by the implemented Dock-owned lifecycle.

The lifecycle is now implemented; see `dock_owned_lifecycle_implementation.md`.
`dock_startup_lifecycle_verification.md` retains the historical before-state.

`desktop/` builds Orbot's floating Tauri/Rust embodiment using the supplied red
shell/blue center image. It starts transparent, borderless, and always on top.
Click to talk, drag to move, and right-click to dock. Conversation has its own
window. It is not a dashboard or a dock station.

`../Orb_Dock_Station_v2.1/` stays outside the Orbot repository. Its React layout
is retained; Tauri/Rust replaces Electron. Window close hides it to its system
tray. The tray restores the station, undocks Orbot, or quits. Docking hides the
floating window after reaching the station and displays Orbot in the bay;
undocking restores the same Orbot process. Browser previews cannot supply these
native window behaviors.

## Services

| Port | Owner | Role |
| --- | --- | --- |
| 16520 | Existing llama.cpp | Local language inference |
| 16521 | Orbot Communication | Conversation, Qwen3-TTS, shared AIMS adapter |
| 16522 | Station Rust host | Window status and show |
| 16523 | Orbot Rust host | Window status, dock, undock |
| 8000 | Station backend | Owner configuration API using the Vault client |

Added listeners bind to loopback. The desktop bridge requires a non-simple
`X-Orbot-Desktop` header and exposes only cosmetic window operations. It grants
no tools, pointer execution, or authority. Loopback is not isolation from other
local programs. Vault collection calls require a server-side credential in
`Orbot_Vault-Logic-System/.local/host-memory.token`, never a frontend credential.
Imported owner authentication remains a development implementation and needs
hardening before broader use.

## Memory contract

- Each new session gets its own AIMS `ShortTermMemory` in RAM. Session caches
  cannot be read by another session and are not restored after process restart.
- Only current-session transient exchanges supply working context. Retained SKG
  records can be recalled across sessions with provenance.
- High priority explicitly promotes an exchange and requested generated audio into
  AIMS long-term memory, with source-session provenance and a retention reason.
- Profile/configuration changes, version history, and uploaded skins have explicit
  deterministic retention rules and use the same Vault writer.
- Authenticated dock API response observations go to session STM, with credential
  fields redacted. Routine diagnostics are not automatically permanent facts.
- High, Medium, and Low have separate bounded working caches. Medium and Low
  receive SKG-guided retention review before purge; see `memory_priority.md`.
- Explicit End Session reviews and clears working memory. Hiding, closing to Dock,
  docking and release do not end the runtime-owned embodiment session. Ordinary
  non-embodiment sessions expire after 30 minutes of inactivity on next
  memory access. There are at most 64 sessions and 256 working items per session.
- Retained records survive session end. An assertion or configuration record is
  not automatically verified truth or an execution grant.

The shared writer is
`Orbot_Vault-Logic-System/AIMS/memory_core/host_sessions.py`. Its ignored data
directory is `Orbot_Vault-Logic-System/.local/host_memory/`. AIMS
`orbot_host.ledger` is authoritative; `host_collections.sqlite` is a rebuildable
projection for lookup. Version preconditions reject conflicting collection
updates. Persistence failure is explicit, with no private dock fallback store.

The station no longer writes private profile/version/conversation/statistics JSON
files or uploaded skin files. Legacy files are not silently imported: migration
requires provenance and schema validation. Seeded conversations/statistics are
no longer returned; legacy simulated execution routes are not mounted.

## Build and verification

### SKG recall wiring

Retained host records now derive provenance-linked A Posteriori Vault atoms.
They start on probation, with assertion authority; saving a memory does not
verify it or promote it to A Priori. The existing AIMS three-domain SKG owns
relationships. Retained items from one session get temporal links; references
to recalled records get context links, not fabricated support/corroboration.
New collection snapshots supersede earlier snapshots in recall while preserving
their immutable history. Missing atom/edge projection work is recovered from
retained ledger records on startup without recreating already-derived atoms.

The orb automatically retrieves a bounded set of relevant saved records before
language generation. Memory is supplied as quoted, unverified data, with a
conservative context budget. The conversation window also has Search saved AIMS
memory for direct recall without calling the LLM. Results show source entry IDs,
atom status, and graph relationships. Current recall is deterministic lexical
matching with SKG relevance weighting, not a semantic-embedding search.

Recall requires a live session. Queries and receipts remain in that session's
RAM; normal searching does not persist private temporary questions in SQLite.
Priority-based closing retention follows `memory_priority.md`. No recall operation grants
execution authority. Knowledge counts are available at
`/memory/knowledge/status`; session-scoped recall uses `/memory/recall`.

Rust/Cargo is installed under `%USERPROFILE%/.cargo/bin` without changing the
global PATH. Add it to the current terminal PATH before Tauri npm commands.
Both projects build with `tauri build --debug --no-bundle`; installers stay
disabled. Start the Communication service before owner configuration operations,
then launch Dock Station, which initializes/attaches services and launches Orbot
docked. Do not launch the Orb executable independently. The station backend uses
`uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000`.

Validated: native builds, live dock/undock transitions, native screenshots
including actual transparent orb rendering, profile read/write through AIMS,
absence of private profile JSON, session start/end, STM isolation/expiry,
retained-record replay, and SQLite rebuild/conflict rejection.

Automatic approval policy blocked deletion of the external dock project's
`.git`. It remains outside Orbot and must not be represented as removed.
