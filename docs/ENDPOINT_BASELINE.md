# ORBS Weaver endpoint baseline

Baseline version: 1.0  
Baseline date: November 1, 2026 (America/Chicago)  
Repository: https://github.com/Spruked/ORBS_Weaver  
Source checkpoint: `cd3175a1d0c25839e9ceae69393bf71d0bdca85b`

This document preserves the endpoint inventory before the next landing-page build increment. It is a reference snapshot, not certification that the listed services work or are running. Listener observations below come from the inventory session and are not continuous monitoring.

## Build priority

Build and design the landing page first, including complete semantic mapping and spatial mapping around an autonomous floating ORB generally 80–200 px in diameter. Its size responds to position and intent. Layout clearance, live element identity, pointer/ping guidance, and observed visitor outcomes must be designed together.

Map the commercial journey toward checkout, a verified sale, and relevant increases in order value. Mapping that journey does not imply that checkout, payment, or upgrade endpoints already exist. Voice integration, secondary pages, and manufacturing expansion follow the accepted landing foundation.

`orbs_vault_system/` is the system's single source of truth. Imported components and their duplicate copies are source material, not separately authorized authorities or deployed services.

## Maintaining this reference

Preserve this baseline when implementation changes. Update [the working endpoint inventory](ENDPOINT_INVENTORY.md) and record additions, removals, changed methods, ports, authentication, source ownership, and verification evidence against this snapshot. Historical defaults are not requirements to start every imported service.

## Baseline endpoint snapshot

Inventory date: November 1, 2026. Static source inventory, supplemented by local TCP listener inspection. No application services were started or mutation endpoints invoked. Defined does not mean running, authenticated, integrated, or production-ready.

Scope: HTTP application routes, service addresses, desktop control routes, and external API dependencies. Ordinary hyperlinks, downloadable assets, Python functions, and Tauri IPC commands are not HTTP endpoints. Vite internal/HMR and third-party framework-generated route internals are not a fixed source-defined API.

## Service addresses

| Service | Default address | Observation |
| --- | --- | --- |
| Website landing preview | http://127.0.0.1:4173 | Listening; static HTTP server |
| AIMS | http://127.0.0.1:8000 | Not listening |
| TPC API | http://127.0.0.1:8003 | Not listening |
| TPC dashboard | http://localhost:5173 | Not listening; Vite may choose another port |
| Orbot web development | http://localhost:8080 | Not listening; binds 0.0.0.0 when started |
| Orbot web preview | http://127.0.0.1:8081 | Not listening |
| Orbot desktop frontend | http://127.0.0.1:1420 | Not listening |
| llama.cpp dependency | http://127.0.0.1:16520 | Listening; API responses not tested in this inventory |
| Communication | http://127.0.0.1:16521 | Not listening |
| External Dock Station | http://127.0.0.1:16522 | Not listening; implementation outside workspace |
| Orbot native desktop control | http://127.0.0.1:16523 | Not listening |
| Cognition/Governance | http://127.0.0.1:16524 | Not listening |
| Motion | http://127.0.0.1:16525 | Not listening |
| Prime Mail dependency | http://127.0.0.1:19000 | Not listening; external implementation |
| VIV dependency | http://127.0.0.1:21000 | Not listening; external implementation |

## AIMS

Base: `http://127.0.0.1:8000`. Source: [AIMS/service.py](../AIMS/service.py).

Duplicate source: Orbot/Orbot_Vault-Logic-System/AIMS/service.py. PORT and AIMS_BIND_HOST can override the address.

| Method | Path | Handler |
| --- | --- | --- |
| GET | `/health` | `health` |
| GET | `/api/v1/status` | `api_status` |
| GET | `/api/v1/memory/summary` | `api_memory_summary` |
| GET | `/api/v1/indexes/status` | `api_indexes_status` |
| GET | `/api/v1/retrievals` | `api_retrievals` |
| POST | `/api/v1/retrievals` | `api_retrieve` |
| GET | `/api/v1/retrievals/{retrieval_id}` | `api_retrieval` |
| POST | `/api/v1/retrievals/{retrieval_id}/feedback` | `api_retrieval_feedback` |
| GET | `/api/v1/skg/status` | `api_skg_status` |
| GET | `/api/v1/skg/activity` | `api_skg_activity` |
| GET | `/api/v1/vault/integrity` | `api_vault_integrity` |
| POST | `/stm/observe` | `observe` |
| GET | `/stm/candidates` | `stm_candidates` |
| POST | `/ltm/commit` | `commit` |
| GET | `/ltm/entry/{entry_id}` | `read_entry` |
| GET | `/ltm/verify` | `verify_ltm` |
| POST | `/vault/apriori` | `add_apriori` |
| POST | `/vault/aposteriori` | `add_aposteriori` |
| POST | `/skg/link` | `link` |
| GET | `/skg/truth` | `truth` |
| GET | `/atom/{atom_id}/trace` | `trace` |
| POST | `/maintenance/run` | `run_maintenance` |
| GET | `/status` | `status` |

## Orbot Communication

Base: `http://127.0.0.1:16521`. Source: [Orbot/runtime/communication/service.py](../Orbot/runtime/communication/service.py).

Defined runtime routes; not observed listening during inventory.

| Method | Path | Handler |
| --- | --- | --- |
| POST | `/voice/input` | `voice_input` |
| POST | `/attention/offer` | `attention_offer` |
| POST | `/sessions` | `start_session` |
| POST | `/sessions/end` | `end_session` |
| GET | `/sessions/{session_id}/caches` | `session_caches` |
| GET | `/presentation/preferences` | `presentation_preferences` |
| POST | `/presentation/preferences` | `save_presentation_preferences` |
| GET | `/voice/preferences` | `voice_preferences` |
| POST | `/voice/preferences` | `save_voice_preferences` |
| GET | `/voice/last-turn` | `last_voice_turn` |
| POST | `/voice/cancel` | `cancel_voice` |
| POST | `/voice/synthesize` | `synthesize_test` |
| POST | `/voice/events` | `voice_client_event` |
| POST | `/sessions/embodiment` | `active_embodiment_session` |
| GET | `/sessions/embodiment` | `current_embodiment_session` |
| POST | `/lifecycle/shutdown` | `shutdown_owned_runtime` |
| GET | `/memory/collections/{name}` | `read_collection` |
| POST | `/memory/collections/{name}` | `write_collection` |
| POST | `/memory/recall` | `recall_memory` |
| GET | `/memory/knowledge/status` | `knowledge_status` |
| POST | `/memory/observations` | `record_observation` |
| GET | `/status` | `status` |
| GET | `/inculcation/status` | `inculcation_status` |
| GET | `/health` | `health` |
| GET | `/diagnostics` | `runtime_diagnostics` |
| POST | `/conversation` | `conversation` |

## Orbot Cognition and Governance

Base: `http://127.0.0.1:16524`. Source: [Orbot/runtime/cognition_governance/service.py](../Orbot/runtime/cognition_governance/service.py).

Defined runtime routes; not observed listening during inventory.

| Method | Path | Handler |
| --- | --- | --- |
| GET | `/health` | `health` |
| POST | `/field/observe` | `observe_field` |
| GET | `/field/status` | `field_status` |
| GET | `/diagnostics` | `runtime_diagnostics` |

## Orbot Motion

Base: `http://127.0.0.1:16525`. Source: [Orbot/runtime/motion/service.py](../Orbot/runtime/motion/service.py).

POST /commands deliberately returns HTTP 503: execution is disabled.

| Method | Path | Handler |
| --- | --- | --- |
| GET | `/health` | `health` |
| POST | `/commands` | `command` |
| POST | `/presentation/authority` | `set_presentation_authority` |
| POST | `/presentation/morbs/assign` | `assign_guidance` |
| POST | `/presentation/morbs/clear` | `clear_guidance` |
| POST | `/presentation/step` | `presentation_step` |
| POST | `/presentation/attention/feedback` | `attention_feedback` |
| GET | `/diagnostics` | `runtime_diagnostics` |

## Triple Predicate Cubed

Base: `http://127.0.0.1:8003`. Source: [Triple_Predicate_Cubed/api/main.py](../Triple_Predicate_Cubed/api/main.py).

Port follows documented launch and UI proxy configuration. Duplicate source: Orbot/Triple_Predicate_Cubed/api/main.py. GET /run-tests runs diagnostics and persists results; it is not a read-only health check.

| Method | Path | Handler |
| --- | --- | --- |
| GET | `/` | `root` |
| GET | `/test` | `test` |
| GET | `/health` | `health` |
| POST | `/reason` | `reason` |
| GET | `/run-tests` | `run_tests` |
| POST | `/transcribe` | `transcribe` |
| POST | `/reason-audio` | `reason_audio` |
| POST | `/speak` | `speak` |

## Framework-generated API documentation

AIMS and both TPC copies use FastAPI defaults: `GET /openapi.json`, `GET /docs`, `GET /docs/oauth2-redirect`, and `GET /redoc`. Orbot Communication, Cognition/Governance, and Motion disable Swagger and ReDoc pages but retain `GET /openapi.json`. These are additional to the explicit application handlers above.

## Native desktop control

Base: `http://127.0.0.1:16523`. Source: [desktop_host.rs](../Orbot/desktop/src-tauri/src/desktop_host.rs). All requests require desktop/launch headers; POST requests additionally require a Vault bearer credential. The status branch matches any non-POST method rather than enforcing GET specifically.

| Method | Path |
| --- | --- |
| GET intended; non-POST branch | `/status` |
| POST | `/dock` |
| POST | `/undock` |
| POST | `/motion/pause` |
| POST | `/motion/resume` |
| POST | `/voice/input-device` |
| POST | `/voice/refresh_devices` |
| POST | `/voice/start` |
| POST | `/voice/pause` |
| POST | `/voice/cancel` |
| POST | `/shutdown` |

## Browser routes and proxies

| Application | Method / route | Status |
| --- | --- | --- |
| Landing preview, 4173 | GET `/` | Static landing page |
| Landing preview, 4173 | HEAD/GET `/<filesystem path>` | Static server serves files beneath workspace root; not an API allowlist |
| Orbot web, 8080/8081 | GET `/` | TanStack page route |
| Orbot dev, 8080 | GET `/__app-env` | Implemented dev middleware |
| Orbot dev, 8080 | GET `/auth/popup?providerId=...` | Middleware exists, but imported src/lib/auth/popup.server.ts is absent |
| Orbot web | GET/POST `/api/rtc` | Client references exist; server handler not found |
| Orbot auth | `/api/auth/*` | Better Auth client/config references; no mounted API handler found; not counted as implemented routes |
| Desktop frontend, 1420 | GET `/` | Vite frontend |
| TPC dashboard, 5173 | GET `/` | React dashboard |
| TPC dashboard, 5173 | `/api/<path>` | Vite strips /api and proxies to localhost:8003/<path>; applies to both TPC copies |

Landing fragment destinations: `/#top`, `/#architecture`, `/#demonstration`, `/#principles`. These are sections on one page, not independent server endpoints.

## External API calls

The following routes are consumed by workspace code; their server implementations are not included here.

| Dependency | Method | Path |
| --- | --- | --- |
| llama.cpp :16520 | GET | `/v1/models` |
| llama.cpp :16520 | GET | `/health` |
| llama.cpp :16520 | GET | `/props` |
| llama.cpp :16520 | POST | `/apply-template` |
| llama.cpp :16520 | POST | `/tokenize` |
| llama.cpp :16520 | POST | `/completion` |
| Dock Station :16522 | GET | `/status` |
| Dock Station :16522 | POST | `/show` |
| Dock Station :16522 | POST | `/release` |
| Dock Station :16522 | POST | `/shutdown` |
| VIV :21000 | GET | `/cali/intelligence/contacts` |
| VIV :21000 | GET | `/cali/intelligence/parties/{party_id}/dossier` |
| VIV :21000 | GET | `/cali/intelligence/contacts/{contact_id}/research` |
| Prime Mail :19000 | GET | `/api/orbot/mail/search` |

Source: [providers.py](../Orbot/runtime/communication/providers.py), [integrations.py](../Orbot/runtime/communication/integrations.py), and desktop_host.rs. Model, VIV, and Mail base URLs are configurable. Remote provider URLs are environment-defined rather than fixed endpoints.

## Vault template declarations

Both `orbs_vault_system/interfaces/api/openapi.yaml` and the retained `Orbot/Orbot_Vault-Logic-System/interfaces/api/openapi.yaml` declare the following routes. They have no corresponding HTTP service implementation or authoritative port in those templates. The README uses localhost:8000 as an example, which overlaps the standalone AIMS default.

| Method | Path | Status |
| --- | --- | --- |
| POST | `/apply` | Specification only |
| GET | `/trace/glyphs` | Specification only |
| GET | `/memory/query` | Specification only |

## Components without their own HTTP service

Correspondence Engine and orb_pointer_human_escalate expose code-level interfaces, not standalone HTTP routes. NATS/ROS bridge subject definitions are messaging contracts, not HTTP endpoints. No checkout, payment, upgrade, or manufacturing HTTP handler was found for the Website ORB landing slice.

Explicit Python application routes: 69 unique service/method/path entries across five service types, plus 31 duplicate definitions in the retained AIMS and TPC copies. Desktop routes, framework documentation routes, external calls, and specification-only routes are listed separately.
