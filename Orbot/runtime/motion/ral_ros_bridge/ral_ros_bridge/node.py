"""Fail-closed ROS<->NATS bridge with injectable I/O.

Swap FakeNats/FakeRos for nats.py + rclpy adapters without changing this contract.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional, Protocol

from .mapping import CmdMapping, MappingTable
from .messages import Envelope, validate_command_envelope


class NatsClient(Protocol):
    def publish(self, subject: str, payload: Dict[str, Any]) -> None: ...
    def subscribe(self, subject: str, handler: Callable[[str, Dict[str, Any]], None]) -> None: ...


class RosClient(Protocol):
    def publish_topic(self, name: str, msg: Dict[str, Any]) -> None: ...
    def send_action(self, name: str, goal: Dict[str, Any], preempt: bool = False) -> None: ...
    def cancel_action(self, name: str) -> None: ...
    def call_service(self, name: str, req: Dict[str, Any]) -> None: ...


class FakeNats:
    def __init__(self) -> None:
        self.published: List[tuple[str, Dict[str, Any]]] = []
        self._subs: Dict[str, List[Callable[[str, Dict[str, Any]], None]]] = {}

    def publish(self, subject: str, payload: Dict[str, Any]) -> None:
        self.published.append((subject, payload))
        for pattern, handlers in self._subs.items():
            if _match(pattern, subject):
                for handler in handlers:
                    handler(subject, payload)

    def subscribe(self, subject: str, handler: Callable[[str, Dict[str, Any]], None]) -> None:
        self._subs.setdefault(subject, []).append(handler)


class FakeRos:
    def __init__(self) -> None:
        self.topics: List[tuple[str, Dict[str, Any]]] = []
        self.actions: List[tuple[str, Dict[str, Any], bool]] = []
        self.cancels: List[str] = []
        self.services: List[tuple[str, Dict[str, Any]]] = []

    def publish_topic(self, name: str, msg: Dict[str, Any]) -> None:
        self.topics.append((name, msg))

    def send_action(self, name: str, goal: Dict[str, Any], preempt: bool = False) -> None:
        self.actions.append((name, goal, preempt))

    def cancel_action(self, name: str) -> None:
        self.cancels.append(name)

    def call_service(self, name: str, req: Dict[str, Any]) -> None:
        self.services.append((name, req))


def _match(pattern: str, subject: str) -> bool:
    p = pattern.split(".")
    s = subject.split(".")
    for i, token in enumerate(p):
        if token == ">":
            return True
        if i >= len(s):
            return False
        if token not in ("*", s[i]):
            return False
    return len(p) == len(s)


class BridgeNode:
    def __init__(
        self,
        robot_id: str,
        nats: NatsClient,
        ros: RosClient,
        world_etag: Optional[str] = None,
        mapping_path: Optional[str] = None,
    ) -> None:
        self.robot_id = robot_id
        self.nats = nats
        self.ros = ros
        self.table = MappingTable(mapping_path) if mapping_path else MappingTable()
        self.world_etag = world_etag
        self.dropped: List[str] = []
        self.nats_connected = True
        self.command_state_stale = False
        self._last_twist_emit = 0.0
        self._pending_twist: Optional[tuple[CmdMapping, Envelope]] = None
        self._last_joint_emit = 0.0

    def start(self) -> None:
        prefix = f"ral.{self.robot_id}."
        self.nats.subscribe(prefix + "cmd.motion.>", self._on_cmd)
        self.nats.subscribe(prefix + "cmd.estop", self._on_cmd)

    def _drop(self, reason: str) -> None:
        self.dropped.append(reason)

    def _on_cmd(self, subject: str, raw: Dict[str, Any]) -> None:
        if self.table.is_forbidden_nats_subject(subject):
            self._drop(f"forbidden subject {subject}")
            return
        try:
            env = validate_command_envelope(raw)
        except (TypeError, ValueError) as exc:
            self._drop(str(exc))
            return
        if env.robot_id != self.robot_id:
            self._drop("robot_id mismatch")
            return
        primitive = str(env.payload.get("primitive_type") or env.payload.get("type") or "")
        if subject.endswith("cmd.estop"):
            primitive = "estop"
        if not primitive:
            self._drop("missing primitive_type")
            return
        mapping = self.table.lookup(primitive)
        if mapping is None:
            self._drop(f"unknown primitive {primitive}")
            return
        if not self.table.subject_matches(mapping, self.robot_id, subject):
            self._drop(f"subject/primitive mismatch: {subject} != {self.table.expected_subject(mapping, self.robot_id)}")
            return
        if mapping.requires_world_etag:
            if env.world_etag is None:
                self._drop("missing world_etag")
                return
            if self.world_etag is None or env.world_etag != self.world_etag:
                self._drop("stale world_etag")
                return
        if mapping.requires_permit and not env.permit_id:
            self._drop("missing execution permit")
            return
        self._dispatch(mapping, env)

    def _dispatch(self, mapping: CmdMapping, env: Envelope) -> None:
        primitive = mapping.primitive_type
        goal = dict(env.payload)
        goal.update({
            "cycle_id": env.cycle_id,
            "proposal_id": env.proposal_id,
            "primitive_id": env.primitive_id,
            "execution_id": env.execution_id,
            "permit_id": env.permit_id,
        })
        if primitive == "estop":
            self._execute_estop(env)
            return
        if primitive == "idle_in_region":
            self.ros.cancel_action("/navigate_to_pose")
            self.ros.publish_topic("/cmd_vel", {"linear": 0, "angular": 0, "zero": True})
            return
        if primitive == "twist_base":
            self._queue_twist(mapping, env)
            return
        ros = mapping.ros
        if ros["kind"] == "action":
            self.ros.send_action(ros["name"], goal, preempt=mapping.preempt)
        elif ros["kind"] == "topic":
            self.ros.publish_topic(ros["name"], goal)
        else:
            self._drop(f"unsupported ROS mapping kind {ros['kind']}")

    def _execute_estop(self, env: Envelope) -> None:
        self._pending_twist = None
        self.ros.call_service("/emergency_stop", {"cycle_id": env.cycle_id})
        self.ros.cancel_action("/navigate_to_pose")
        self.ros.cancel_action("/arm_controller/follow_joint_trajectory")
        self.ros.publish_topic("/cmd_vel", {"linear": 0, "angular": 0, "zero": True})

    def _queue_twist(self, mapping: CmdMapping, env: Envelope) -> None:
        self._pending_twist = (mapping, env)
        self.flush_twist()

    def flush_twist(self, now: Optional[float] = None) -> bool:
        if self._pending_twist is None:
            return False
        mapping, env = self._pending_twist
        current = time.monotonic() if now is None else now
        max_hz = mapping.max_hz or 20.0
        period = 1.0 / max_hz
        if self._last_twist_emit and current - self._last_twist_emit < period:
            return False
        goal = dict(env.payload)
        goal.update({"cycle_id": env.cycle_id, "primitive_id": env.primitive_id, "permit_id": env.permit_id})
        self.ros.publish_topic(mapping.ros["name"], goal)
        self._last_twist_emit = current
        self._pending_twist = None
        return True

    def on_joint_states(self, msg: Dict[str, Any], now: Optional[float] = None) -> bool:
        current = time.monotonic() if now is None else now
        if self._last_joint_emit and current - self._last_joint_emit < 1.0 / 50.0:
            return False
        self._last_joint_emit = current
        self.nats.publish(
            f"ral.{self.robot_id}.tel.motion.joints",
            {
                "robot_id": self.robot_id,
                "schema": "tti.tel.joints.v2",
                "payload": {key: value for key, value in msg.items() if key != "effort"},
            },
        )
        return True

    def update_world_etag(self, etag: str) -> None:
        self.world_etag = str(etag)
        self.command_state_stale = False

    def on_nats_disconnect(self) -> None:
        self.nats_connected = False
        self.command_state_stale = True
        self._pending_twist = None
        self.ros.cancel_action("/navigate_to_pose")
        self.ros.publish_topic("/cmd_vel", {"linear": 0, "angular": 0, "zero": True})

    def on_nats_reconnect(self) -> None:
        self.nats_connected = True
        self.nats.publish(
            f"ral.{self.robot_id}.tel.health",
            {"robot_id": self.robot_id, "schema": "tti.tel.health.v2", "payload": {"status": "command_state_stale"}},
        )

    def on_joints_timeout(self) -> None:
        if not self.nats_connected:
            return
        self.nats.publish(
            f"ral.{self.robot_id}.tel.health",
            {"robot_id": self.robot_id, "schema": "tti.tel.health.v2", "payload": {"status": "actuators_lost"}},
        )
