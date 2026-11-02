# ral_ros_bridge

Dumb, fail-closed I/O between the **NATS mission / skill bus** and **ROS 2** drivers, TF, controllers, Nav2, MoveIt, and ros2_control.

The bridge does **not** run Core-4, does **not** run Hard Admission, and does **not** listen to an LLM account. It translates only allow-listed, already-admitted execution primitives into ROS interfaces, rate-limits telemetry, and preserves execution provenance.

```text
TTI / RAL         = intent and world-state reasoning
Core-4            = cognitive tribunal
Hard Admission    = non-negotiable runtime gate
Execution Permit  = short-lived authority artifact
NATS / JetStream  = mission, execution and audit bus
ROS 2             = physics, drivers, actions and topics
PLC / STO         = independent hard safety
```

## Absolute execution rule

Normal motion commands require a valid command envelope containing a current `permit_id`, `world_etag`, execution identity, and unexpired permit timestamp. The bridge never invents authority and never upgrades an invalid command into a valid one.

`cmd.estop` is the only command intentionally allowed to bypass the ordinary execution-permit requirement; it remains constrained by the dedicated NATS ACL and mirrors a stop into ROS while the independent PLC/STO path remains authoritative for hard power safety.

## Layout

```text
ral_ros_bridge/
├── README.md
├── SPEC.md
├── mapping.yaml
├── subjects.yaml
├── rates.yaml
├── nats/accounts.conf
├── schemas/
│   ├── envelope.json
│   └── command_envelope.json
├── ral_ros_bridge/
│   ├── __init__.py
│   ├── messages.py
│   ├── mapping.py
│   ├── node.py
│   └── demo.py
└── tests/test_contract.py
```

## Run the reference stub

```bash
python -m ral_ros_bridge.demo
python -m unittest discover -s tests -v
```

Requires Python 3.10+ and PyYAML. The reference implementation uses injectable I/O and in-memory fakes; the transport-binding step replaces the fakes with `nats.py` + `rclpy` without changing the admission, mapping, subject, or failure contracts.
