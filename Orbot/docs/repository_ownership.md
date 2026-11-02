# Repository ownership and implementation scope

The subsequent Dock-owned startup phase is implemented in these same separate
repositories. Current ownership and native results are documented in Orbot's
`dock_owned_lifecycle_implementation.md` and Dock's
`docs/dock_owned_startup_implementation.md`. Test counts below describe the
original inculcation phase, not the expanded lifecycle regression suite.

Verified October 28, 2026. `Desktop_System` is a workspace containing separate
Git repositories, not a combined repository or monorepo.

| Local root relative to Desktop_System | Verified origin | Branch | Working tree |
| --- | --- | --- | --- |
| `Orbot/Orbot` | `https://github.com/Spruked/Orbot.git` | `main` | Modified and untracked files; includes pre-existing work and the inculcation implementation |
| `Orbot/Orb_Dock_Station_v2.1` | `https://github.com/Spruked/Orb_Dock_Station_v2.1.git` | `main` | Modified, deleted and untracked files; most changes predate the inculcation work |
| `VIV` | `https://github.com/Spruked/VIV.git` | `main` | Clean |
| `SPRUK_EMAIL` | `https://github.com/Spruked/SPRUK_EMAIL.git` | `main` | Clean |

The immediate implementation target is `Spruked/Orbot`. Active professional
education, compiler/loader, cognition integration, AIMS lifecycle changes and
their tests belong here. No commits or pushes were made.

Lifecycle ownership clarification: Dock is the primary launch/activation
environment and Orbot must initially dock there. Separate Git ownership and
native processes do not imply independent user launch. See
`dock_startup_lifecycle_verification.md` for intended behavior versus current code.

The legacy reference belongs to the independent repository
`Spruked/Orb_Assistant_Desktop_2026`. Its v1.1 file was retrieved at commit
`63f5eac23a99cde219a3847bb1293442863c3b43` from
`mcp/orb_desktop_mcp/orb_cognition/Desktop_ORB_Professional_Inculcation_v1.1.md`.
It was not merged into Orbot. The complete reference snapshot and provenance
metadata are under `inculcation/references/`. No local checkout, branch or
working-tree state is asserted for that remote-only reference repository.

## Separate companion changes

The completed inculcation task also added a read-only Dock integration within
Dock's own repository: an authenticated status route, a diagnostics telemetry
section and three tests. Its owning report is
`../Orb_Dock_Station_v2.1/docs/inculcation_companion_integration.md`.
These are companion changes, not Orbot source changes or prerequisites for
Orbot's loader. Existing Dock changes must not be attributed to this task.

Orbot owns 98 of the 101 reported executed tests: 32 Communication, 48 runtime,
8 Core-4/admission and 10 bridge tests. Dock owns the other 3 tests.

## External integration requirements

- VIV retains contacts, relationships, dossiers, research and evidence. Orbot
  integration must use its published authenticated API; no direct database
  mutation or second contact authority is authorized by inculcation.
- Prime Mail retains messages, mailboxes, attachments and custody. Future Orbot
  integration must use an authenticated, appropriately scoped published API.
  The baseline assessment found ordinary Mail API authentication incomplete;
  inculcation does not fix or authorize bypassing that boundary.
- Dedicated Orbot VIV/Mail adapters and scoped integration credentials remain
  requirements, not implemented capabilities. VIV and Prime Mail were unchanged.
- The shared llama.cpp launcher/configuration is machine-level service state,
  outside these repository implementations. Its administrator-applied context
  change does not give Orbot ownership of the service or its slots.

Any later source changes, tests and commits must be scoped to their owning
repository. Cross-repository integration requirements should be reported
separately. Do not merge repositories or relocate AIMS to accommodate them.
