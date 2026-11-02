# Diagnostics implementation progress

The first implementation connects producer `/diagnostics` routes on Communication,
Cognition/Governance and Motion to the external Dock backend's authenticated
`GET /diagnostics/snapshot`. The Dock Diagnostics panel polls every five seconds,
shows all twelve specification areas, source and measurement time, and marks
measurements stale after fifteen seconds. It preserves stale values separately.

Measured now: producer process presence/PID, instance identity, elapsed instance
uptime, heartbeat timestamp, Motion disabled state/reason, current field diagnostics,
Dock backend presence/instance uptime, disk capacity/free bytes for existing
Vault, AIMS and model paths. Instance startup time is not claimed as OS process
creation time or historical restart evidence. Startup validation remains unknown.

Absent producers mean unknown, not stopped. Unsupported measurements remain
unknown. GPU/CPU/RAM, model/speech performance, microphone telemetry, full memory
metrics, grants/permits, verified execution, security counters and the correlated
activity stream remain to be connected. Field seed remains unknown for existing
runs. Existing legacy health routes are not the new measurement contract.

Diagnostics polling bypasses the frontend's AIMS-session prerequisite and backend
response-capture middleware, so inspecting health does not depend on writing a
diagnostic observation into AIMS. Snapshot access requires Dock owner authentication.

Validation: seven runtime tests pass; Dock auth rejection, disconnected-producer
unknown states, all twelve sections, and real disk measurements pass with the Dock
Python environment. Dock frontend production build passes (bundle-size advisory).
Live UI/native application validation and runtime reload remain pending.

External Dock files changed: backend services/diagnostics_snapshot.py,
routers/diagnostics.py, services/collection_capture.py; frontend services/api.js
and panels/Diagnostics.jsx. These live outside the main Orbot Git repository.
