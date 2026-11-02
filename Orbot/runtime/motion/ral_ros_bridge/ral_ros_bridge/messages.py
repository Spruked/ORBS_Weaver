from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Union
import time

CycleId = Union[str, int]


@dataclass(frozen=True)
class RobotTime:
    sec: int
    nsec: int


@dataclass(frozen=True)
class Envelope:
    event_id: str
    robot_id: str
    cycle_id: CycleId
    schema: str
    payload: Dict[str, Any]
    task_id: str = "unknown"
    proposal_id: Optional[str] = None
    primitive_id: Optional[str] = None
    execution_id: Optional[str] = None
    permit_id: Optional[str] = None
    permit_expires_at: Optional[float] = None
    priority: str = "normal"
    robot_time: Optional[RobotTime] = None
    world_etag: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "event_id": self.event_id,
            "robot_id": self.robot_id,
            "task_id": self.task_id,
            "cycle_id": self.cycle_id,
            "proposal_id": self.proposal_id,
            "primitive_id": self.primitive_id,
            "execution_id": self.execution_id,
            "permit_id": self.permit_id,
            "permit_expires_at": self.permit_expires_at,
            "schema": self.schema,
            "priority": self.priority,
            "world_etag": self.world_etag,
            "payload": self.payload,
        }
        if self.robot_time:
            data["robot_time"] = {"sec": self.robot_time.sec, "nsec": self.robot_time.nsec}
        return data


def validate_envelope(raw: Dict[str, Any]) -> Envelope:
    missing = [k for k in ("event_id", "robot_id", "cycle_id", "schema", "payload") if k not in raw]
    if missing:
        raise ValueError(f"invalid envelope, missing {missing}")
    cycle = raw["cycle_id"]
    if not isinstance(cycle, (str, int)) or isinstance(cycle, bool) or str(cycle) == "":
        raise ValueError("cycle_id must be a non-empty string or integer")
    if not isinstance(raw["payload"], dict):
        raise ValueError("payload must be an object")
    rt = raw.get("robot_time")
    robot_time = None
    if rt is not None:
        if not isinstance(rt, dict) or "sec" not in rt or "nsec" not in rt:
            raise ValueError("robot_time must contain sec and nsec")
        robot_time = RobotTime(sec=int(rt["sec"]), nsec=int(rt["nsec"]))
    expires = raw.get("permit_expires_at")
    return Envelope(
        event_id=str(raw["event_id"]),
        robot_id=str(raw["robot_id"]),
        cycle_id=cycle,
        schema=str(raw["schema"]),
        payload=dict(raw["payload"]),
        task_id=str(raw.get("task_id", "unknown")),
        proposal_id=_opt_str(raw.get("proposal_id")),
        primitive_id=_opt_str(raw.get("primitive_id")),
        execution_id=_opt_str(raw.get("execution_id")),
        permit_id=_opt_str(raw.get("permit_id")),
        permit_expires_at=None if expires is None else float(expires),
        priority=str(raw.get("priority", "normal")),
        robot_time=robot_time,
        world_etag=None if raw.get("world_etag") is None else str(raw["world_etag"]),
    )


def validate_command_envelope(raw: Dict[str, Any], *, allow_unpermitted_estop: bool = True, now: Optional[float] = None) -> Envelope:
    env = validate_envelope(raw)
    primitive = str(env.payload.get("primitive_type") or env.payload.get("type") or "")
    is_estop = primitive == "estop" or env.priority == "estop"
    if is_estop and allow_unpermitted_estop:
        return env
    missing = [
        name for name, value in (
            ("proposal_id", env.proposal_id),
            ("primitive_id", env.primitive_id),
            ("execution_id", env.execution_id),
            ("permit_id", env.permit_id),
            ("permit_expires_at", env.permit_expires_at),
            ("world_etag", env.world_etag),
        ) if value is None or value == ""
    ]
    if missing:
        raise ValueError(f"command missing permit provenance {missing}")
    current = time.time() if now is None else now
    assert env.permit_expires_at is not None
    if env.permit_expires_at <= current:
        raise ValueError("execution permit expired")
    return env


def _opt_str(value: Any) -> Optional[str]:
    return None if value is None else str(value)
