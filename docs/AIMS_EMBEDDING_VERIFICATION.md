# AIMS embedded memory verification

## Source checkpoints

Original consolidated source: `cd3175a1d0c25839e9ceae69393bf71d0bdca85b`.

Historical endpoint baseline commit: `4d49f0ce941d215c9fba6b2a4f83200fe6dec73a`.
That commit records the original endpoint baseline and its build-baseline link,
before the implementation changes. The implementation commit follows it and is
identifiable by `git log --all --grep="Remove standalone AIMS HTTP servers"`.

## Verified removal and preservation

- Both standalone `AIMS/service.py` files are deleted, along with their
  HTTP-wrapper-only `test_service_security.py` tests.
- Both AIMS package manifests and requirements remove FastAPI, Uvicorn, and
  Pydantic requirements. Optional GraphQLite support remains unchanged.
- Both AIMS READMEs replace listener startup/configuration and HTTP routes with
  embedded-library usage. Hardening contracts assign host security responsibilities
  to the trusted host rather than requiring an AIMS HTTP listener.
- No reusable `memory_core` implementation file changed in either copy.
- Canonical authority remains `orbs_vault_system`. AIMS stores and retrieves
  evidence; it does not independently approve business facts.
- Reviewed workspace launch paths: `Orbot/startup.sh`, package scripts,
  `Orbot/scripts/setup-communication.ps1`, `runtime/supervisor.py`, and runtime
  `main.py` entrypoints. No separate AIMS startup command remains. The supervisor
  registry contains only communication 16521, cognition_governance 16524, and
  motion 16525. The existing memory adapter imports `HostMemory` directly.
- Unrelated service implementations and ports are unchanged, including Station
  backend documentation and generic Vault API examples referencing port 8000.
- `docs/ENDPOINT_BASELINE.md` is byte-for-byte unchanged from the baseline commit.
  Current removal status is recorded only in the working inventory and this report.

## Executed tests

| Working directory | Command | Result |
| --- | --- | --- |
| AIMS | `python -B -S -m unittest discover -s tests -v` | 13 passed, 2 skipped |
| Orbot/Orbot_Vault-Logic-System/AIMS | `python -B -S -m unittest discover -s tests -v` | 13 passed, 2 skipped |
| Orbot | `python -B -m unittest discover -s runtime/communication/tests -p test_memory.py -v` | 5 passed |
| Orbot | `python -B -m unittest discover -s runtime/communication/tests -p test_knowledge.py -v` | 5 passed |
| Orbot | `python -B -m unittest discover -s runtime/communication/tests -p test_priority.py -v` | 7 passed |
| Orbot | `python -B -m unittest discover -s runtime/communication/tests -p test_provider_memory.py -v` | 3 passed |
| Workspace root | `python -B scripts/verify_aims_embedding.py` | Both copies passed |

Total unittest results: 46 passed, 4 skipped, no failures. The skipped tests require
the optional GraphQLite accelerator. `-S` disables site-packages for the two core
suites. The embedding smoke check imports and instantiates each library with
socket binding blocked, confirms no HTTP dependencies were imported, checks
separate customer stores, reopens persisted memory, and verifies ledger integrity.
All test data is temporary; existing customer data is not used or migrated.

## Remaining integration limits

- Both reusable AIMS copies remain; consolidating their differing library code is
  outside this removal. Orbot still imports its bundled copy.
- Host configuration must validate customer identities and keep isolated stores
  beneath the canonical Vault boundary. Explicit existing storage overrides are
  retained; this change does not migrate or certify real customer stores.
- Optional GraphQLite functionality is not verified in this environment.
- Removing the HTTP wrappers does not implement missing manufacturing, commercial
  approval, checkout, or production security capabilities.
- No unrelated service was started, stopped, renumbered, or live-tested for this
  verification. The landing-page-first build sequence remains unchanged.

## Implementation files

Changes cover both AIMS READMEs, hardening contracts, package manifests, and
requirements; deletion of both HTTP wrappers and their server-only tests;
`orbs_vault_system/AUTHORITY.md`; `docs/ENDPOINT_INVENTORY.md`; this verification
report; and `scripts/verify_aims_embedding.py`. The historical baseline is not
part of the implementation diff. Use `git show --name-status` on the implementation
commit for the exact list.
