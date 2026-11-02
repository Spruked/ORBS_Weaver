"""Mapping-table loader. mapping.yaml is the single source of truth."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

DEFAULT_MAPPING_PATH = Path(__file__).resolve().parents[1] / "mapping.yaml"


@dataclass(frozen=True)
class CmdMapping:
    primitive_type: str
    subject: str
    ros: Dict[str, Any]
    coalesce: str
    max_hz: Optional[float]
    preempt: bool
    requires_cycle_id: bool
    requires_world_etag: bool
    requires_permit: bool
    bodies: List[str]


class MappingTable:
    def __init__(self, path: Path | str = DEFAULT_MAPPING_PATH) -> None:
        self.path = Path(path)
        raw = yaml.safe_load(self.path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("mapping.yaml must contain an object")
        self.version = int(raw.get("version", 0))
        self.robot_id_token = str(raw.get("robot_id_token", "{robot_id}"))
        self.by_primitive: Dict[str, CmdMapping] = {}
        for row in raw.get("nats_to_ros", []):
            mapping = CmdMapping(
                primitive_type=str(row["primitive_type"]),
                subject=str(row["subject"]),
                ros=dict(row["ros"]),
                coalesce=str(row.get("coalesce", "none")),
                max_hz=None if row.get("max_hz") in (None, "events") else float(row["max_hz"]),
                preempt=bool(row.get("preempt", False)),
                requires_cycle_id=bool(row.get("requires_cycle_id", True)),
                requires_world_etag=bool(row.get("requires_world_etag", False)),
                requires_permit=bool(row.get("requires_permit", False)),
                bodies=list(row.get("bodies", [])),
            )
            if mapping.primitive_type in self.by_primitive:
                raise ValueError(f"duplicate primitive {mapping.primitive_type}")
            self.by_primitive[mapping.primitive_type] = mapping
        forbidden = raw.get("forbidden", {})
        self.forbidden_ros = tuple(forbidden.get("ros_topics_never_forward", []))
        self.forbidden_nats_sub = tuple(forbidden.get("nats_subjects_bridge_must_not_subscribe", []))

    def lookup(self, primitive_type: str) -> Optional[CmdMapping]:
        return self.by_primitive.get(primitive_type)

    def expected_subject(self, mapping: CmdMapping, robot_id: str) -> str:
        return mapping.subject.replace(self.robot_id_token, robot_id)

    def subject_matches(self, mapping: CmdMapping, robot_id: str, actual: str) -> bool:
        return self.expected_subject(mapping, robot_id) == actual

    def is_forbidden_ros(self, topic: str) -> bool:
        return topic in self.forbidden_ros

    def is_forbidden_nats_subject(self, subject: str) -> bool:
        return any(_subject_pattern_matches(pattern, subject) for pattern in self.forbidden_nats_sub)


def _subject_pattern_matches(pattern: str, subject: str) -> bool:
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


def lookup_cmd(primitive_type: str) -> Optional[CmdMapping]:
    return MappingTable().lookup(primitive_type)
