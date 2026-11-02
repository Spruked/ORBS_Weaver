# Three Orbot runtimes

Run from the repository root using the installed Communication environment:

```powershell
runtime/communication/.venv/Scripts/python.exe -m runtime.supervisor
```

Stop the existing standalone Communication process first. The supervisor refuses
occupied ports and never starts a second writer alongside it. Ctrl+C requests
graceful shutdown, including AIMS session review. Forced termination can still
lose pending temporary memories. If one child exits, its peers stop.

| Runtime | Port | Current ownership |
| --- | --- | --- |
| Communication | 16521 | Orb/dock ingress, conversation, interchangeable LLM adapters, Qwen3-TTS 1.7B, memory API |
| Cognition/Governance | 16524 | Deterministic Core-4 evaluation, RAL contracts and admission prototype under `ral_core/` |
| Motion | 16525 | Disabled command ingress; ROS/NATS bridge prototype under `ral_ros_bridge/` |

Each can run independently with `python -m runtime.<name>.main`. Each exposes
`GET /health`; Communication `/status` reports peer availability. A healthy
process does not imply production execution authority.

In the unified ORBS Weaver workspace, `../orbs_vault_system/` is the sole record
authority; its `AUTHORITY.md` supersedes historical ownership statements here.
`Orbot_Vault-Logic-System/` retains implementation/reference code. Its existing AIMS
writer is currently hosted in Communication through `communication/memory.py`;
the other runtimes must not open additional writers. Moving that foundation to
Cognition/Governance requires a versioned authenticated API migration, not a
second memory instance. The dock remains outside this repository and uses this
same memory API.

This change organizes and launches the runtimes. Full RAL orchestration,
canonical Vault permits, scheduler-to-motion delivery, and independent
correspondence verification remain implementation work in `docs/wiring_plan.md`.
Core-4's typed `evaluate()` is internal and advisory; no public endpoint accepts
caller-supplied authority or World State. Motion `/commands` always rejects.
The old admission and bridge examples are test prototypes, not live authority.
The floating Tauri Orb is an embodiment, not a fourth runtime.

## VIV and Prime Mail read integration

The owner can explicitly request a lookup with `search my mail for ...` or
`search VIV for ...` in voice or text conversation. Communication reads Mail
through `GET /api/orbot/mail/search` and VIV through its authenticated contacts,
dossier, and research APIs. Mail results remain correspondence records; VIV
research verification labels are carried into the model context. Raw lookup
results are not copied into another AIMS collection.

The runtime uses these inherited process settings:

| Setting | Default / owner |
| --- | --- |
| `ORBOT_VIV_API_URL` | `http://127.0.0.1:21000` |
| `CALI_ORBOT_API_TOKEN` | Dedicated read credential configured in VIV |
| `ORBOT_MAIL_API_URL` | `http://127.0.0.1:19000` |
| `ORBOT_MAIL_API_TOKEN` | Dedicated read credential configured in Prime Mail |

Both credentials must be distinct, at least 32 characters, and remain outside source
control. This integration reads contact/dossier/research records and mail
messages. It does not send mail, create VIV research, change verification state,
or issue execution permits. Attachments are not exposed to Orbot yet.

## Desktop attention

The native Windows host sends the Motion Runtime the foreground process/window
bounds, the system's last-input idle duration, and Orbot's current voice state.
The Motion Runtime observes a stable application, guides Orbot to a nearby
position outside that window when one is available, and holds there. It can
request one short local spoken invitation after the owner has paused and
hands-free listening is active. The local language and Qwen speech services
create that invitation without adding a synthetic owner turn to AIMS. Foreground
titles are transient context and are not persisted. Declines suppress another
offer for an hour; an unanswered offer expires into a 20-minute quiet period.
Attention observation stops while Dock/Orbot is foreground. Shape variation is
disabled; sphere, liquid, and hexagon remain manually selectable.

## Validation

```powershell
$python = 'runtime/communication/.venv/Scripts/python.exe'
& $python -B -m unittest discover -s runtime/communication/tests
& $python -B -m unittest discover -s runtime/tests
$env:PYTHONPATH = 'runtime/cognition_governance/ral_core'
& $python -B -m unittest discover -s runtime/cognition_governance/ral_core/tests
& $python -B -m unittest discover -s runtime/motion/ral_ros_bridge/tests
```
