# ral_ros_bridge — execution contract

**TTI/RAL proposes and coordinates. Core-4 judges. Hard Admission grants permission. The Execution Fabric dispatches. ROS 2 executes physics. PLC/STO owns independent hard safety.**

The bridge is deliberately a dumb I/O boundary. `mapping.yaml` is the executable allow-list: if a primitive is absent, the bridge drops it.

---

## 1. Role

The bridge is a ROS 2 boundary node that:

1. Subscribes to a fixed set of ROS topics/actions used for robot state and execution.
2. Publishes downsampled metadata onto NATS `tel.*` subjects and selected WorldState updates.
3. Subscribes only to admitted motion subjects and `cmd.estop`.
4. Forwards only allow-listed primitives to ROS actions/topics/services.
5. Rejects stale, expired, malformed, wrong-subject, wrong-robot, or unpermitted commands.
6. Stops bounded motion if the NATS command path disappears; it never fabricates telemetry when ROS state disappears.

It does **not**:

- call Core-4
- perform Hard Admission
- issue Execution Permits
- subscribe to proposals
- subscribe to tool or speech commands
- infer a missing primitive
- carry raw camera, depth, point-cloud, or high-rate torque streams on NATS
- replace the PLC, STO, drive interlocks, or hardware e-stop

---

## 2. Command provenance

Every normal `cmd.motion.*` envelope carries:

| Field | Rule |
|---|---|
| `event_id` | unique event identifier |
| `robot_id` | must match the bridge robot and subject token |
| `task_id` | owning RAL task or `reflex` |
| `cycle_id` | opaque RAL cycle identifier; string or integer accepted and normalized |
| `proposal_id` | originating action proposal |
| `primitive_id` | exact admitted execution primitive |
| `execution_id` | execution-fabric instance |
| `permit_id` | Execution Permit that authorized this primitive |
| `permit_expires_at` | UTC epoch seconds; must be in the future at dispatch |
| `schema` | e.g. `tti.motion_cmd.v2` |
| `priority` | `estop`, `safety`, `user_interrupt`, `task_critical`, `normal`, or `ambient` |
| `robot_time` | ROS clock stamp when available |
| `world_etag` | WorldState/KV revision bound to the permit; required on normal command |
| `payload` | primitive-specific arguments |

The bridge treats `permit_id` as required provenance, not as permission it may fabricate. Network ACLs ensure only the Execution Dispatcher can publish admitted `cmd.*`. The bridge performs cheap final checks: permit fields present, permit not expired, subject/primitive match, robot match, and `world_etag` equals the locally watched WorldState revision.

`cmd.estop` is exempt from the normal permit requirement so a trusted safety stop is never delayed by ordinary admission plumbing. It still requires the dedicated authenticated NATS subject and never replaces PLC/STO.

Join key for robot-side evidence and mission-side audit is `(robot_id, cycle_id, execution_id, robot_time)`.

---

## 3. Subject tree

See `subjects.yaml`.

Key boundaries:

- `ral.{robot}.cycle.{cycle}.proposal` — proposer / planner domain
- `ral.{robot}.cycle.{cycle}.verdict` — Core-4 result
- `ral.{robot}.cycle.{cycle}.admission` — Hard Admission request/result domain
- `ral.{robot}.cycle.{cycle}.permit` — issued Execution Permit metadata
- `ral.{robot}.cmd.motion.>` — admitted motion lane consumed by bridge
- `ral.{robot}.cmd.estop` — dedicated software stop mirror
- `ral.{robot}.tel.>` — bridge telemetry
- `ral.{robot}.ws.changed` — WorldState revision notification

The bridge does not subscribe to proposal, verdict, permit, speech, or tool subjects. It only receives already-dispatched motion commands plus estop.

---

## 4. NATS → ROS allow-list

Source of truth: `mapping.yaml`.

| primitive | ROS interface | behavior |
|---|---|---|
| `twist_base` | `/cmd_vel` `geometry_msgs/Twist` | 20 Hz cap, latest sample wins |
| `nav_to_pose` | Nav2 `NavigateToPose` | one active base goal, newer cycle preempts |
| `focus_on` | head `FollowJointTrajectory` | target already solved upstream |
| `arm_follow` | arm `FollowJointTrajectory` | one active arm goal, newer cycle preempts |
| `gripper_set` | `GripperCommand` | bounded gripper action |
| `idle_in_region` | cancel Nav2 + zero twist | deterministic safe/idle primitive |
| `estop` | `/emergency_stop` + cancel + zero twist | software mirror; PLC/STO remains independent |

The bridge verifies that the primitive is valid **for the exact NATS subject**. A valid primitive sent on the wrong body subject is dropped.

Unknown primitive → log + drop. Never best-effort guess.

---

## 5. ROS → NATS telemetry

| ROS source | NATS / WorldState | default max rate |
|---|---|---|
| `/joint_states` | `tel.motion.joints` | 50 Hz; omit effort unless explicitly allow-listed |
| TF `base_link`, `ee_link` | `tel.motion.pose` + watched WorldState pose keys | 10 Hz |
| perception detections | `tel.perception.camera.meta` | 10 Hz metadata only |
| Nav2 status | `tel.nav` | event-driven |
| `/diagnostics` | `tel.health` | 1 Hz |
| `/clock` | envelope `robot_time` | stamp only |

Raw camera frames, depth, point clouds, and high-rate controller streams stay inside the robotics transport.

---

## 6. Backpressure and coalescing

- Twist commands are latest-wins, not FIFO. If several arrive inside a 20 Hz window, only the newest pending sample is eligible at the next flush.
- Nav/head/arm/gripper actions are bounded by body-domain concurrency rules.
- Telemetry is downsampled before NATS publication.
- E-stop has no coalescing delay.
- Joint telemetry is not persisted to the `RAL_CYCLES` stream.

---

## 7. Failure and reflex behavior

| Event | Bridge behavior |
|---|---|
| NATS command path disconnect | cancel Nav2, zero `/cmd_vel`, mark local command-state stale; emit stale/health telemetry after connectivity returns |
| `/joint_states` silent beyond configured watchdog | emit `actuators_lost` if NATS is available; never fabricate joint state |
| stale `world_etag` vs locally watched revision | drop command |
| missing normal-command permit provenance | drop command |
| expired permit | drop command |
| subject/primitive mismatch | drop command |
| malformed envelope / missing cycle id | drop command |
| LLM or Planner attempts `cmd.*` | NATS ACL rejects; bridge also rejects malformed/unpermitted traffic that reaches it |

The watchdog durations in `rates.yaml` are defaults and must be tuned per robot/controller rates; they are not universal safety-certification values.

---

## 8. NATS authority accounts

See `nats/accounts.conf`.

| Account | Role |
|---|---|
| `LLM` | proposal publication only; never `cmd.*` |
| `PLANNER` | RAL planning and proposal/admission requests; never `cmd.*` |
| `TRIBUNAL` | Core-4 verdicts |
| `ADMISSION` | Hard Admission + permit issue/reject events |
| `EXECUTOR` | the only ordinary software account allowed to publish `cmd.motion.*`, `cmd.speech`, and `cmd.tool.*`, and only from valid permits |
| `BRIDGE` | consume admitted motion/estop; publish bounded telemetry |
| `TOOL_WORKERS` | consume admitted tool commands |

This preserves the software authority chain:

```text
Proposal → Core-4 → Hard Admission → Execution Permit → Execution Dispatcher → cmd.* → Bridge/Workers
```

No model or planner account can sign actuator commands.

---

## 9. Audit / replay

- `rosbag2` records robot-side actions and sensor streams.
- JetStream `RAL_CYCLES` records proposal, verdict, admission/permit, non-streaming command envelopes, execution receipts, and selected state transitions.
- WorldState KV carries the current technical state/revision.
- Twist samples and high-rate joint telemetry are not persisted in the mission audit stream.

---

## 10. Out of scope for this bridge

- Core-4 implementation
- Hard Admission implementation
- Execution Permit issuer
- TTS / speech arbitration
- MCP tool workers
- fleet / leaf-node topology
- replacing ROS middleware (`rmw` remains a ROS concern)
