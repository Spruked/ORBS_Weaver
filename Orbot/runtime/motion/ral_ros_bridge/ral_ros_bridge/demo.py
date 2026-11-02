"""In-memory bridge contract demonstration; no ROS or nats-server required."""

from __future__ import annotations

import time

from .messages import Envelope
from .node import BridgeNode, FakeNats, FakeRos


def _env(cycle: int, primitive: str, **payload) -> dict:
    now = time.time()
    return Envelope(
        event_id=f"e{cycle}",
        robot_id="orbot-07",
        task_id="demo-task",
        cycle_id=cycle,
        proposal_id=f"proposal-{cycle}",
        primitive_id=f"primitive-{cycle}",
        execution_id=f"execution-{cycle}",
        permit_id=f"permit-{cycle}",
        permit_expires_at=now + 30.0,
        schema="tti.motion_cmd.v2",
        payload={"primitive_type": primitive, **payload},
        world_etag="118",
    ).to_dict()


def main() -> None:
    nats = FakeNats()
    ros = FakeRos()
    node = BridgeNode("orbot-07", nats, ros, world_etag="118")
    node.start()

    nats.publish("ral.orbot-07.cmd.motion.head", _env(42, "focus_on", frame="ee_link"))
    assert any(action[0] == "/head_controller/follow_joint_trajectory" for action in ros.actions)

    nats.publish(
        "ral.orbot-07.cmd.estop",
        Envelope(event_id="stop", robot_id="orbot-07", cycle_id=43, schema="tti.estop.v1", priority="estop", payload={"primitive_type": "estop"}).to_dict(),
    )
    assert ros.services and ros.services[0][0] == "/emergency_stop"

    stale = _env(44, "nav_to_pose")
    stale["world_etag"] = "99"
    nats.publish("ral.orbot-07.cmd.motion.base", stale)
    assert any("stale world_etag" in reason for reason in node.dropped)

    missing_permit = _env(45, "nav_to_pose")
    missing_permit["permit_id"] = None
    nats.publish("ral.orbot-07.cmd.motion.base", missing_permit)
    assert any("permit provenance" in reason for reason in node.dropped)

    node.on_joint_states({"name": ["j1"], "position": [0.1], "effort": [9]}, now=10.0)
    telemetry = [payload for subject, payload in nats.published if subject.endswith("tel.motion.joints")]
    assert telemetry and "effort" not in telemetry[-1]["payload"]

    node.on_nats_disconnect()
    assert any(message.get("zero") for topic, message in ros.topics if topic == "/cmd_vel")

    print("ral_ros_bridge demo: contract checks passed")
    print(f"actions={len(ros.actions)} topics={len(ros.topics)} services={len(ros.servicer)} dropped={node.dropped}")


if __name__ == "__main__":
    main()
