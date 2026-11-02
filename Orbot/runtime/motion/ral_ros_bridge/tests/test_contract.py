from __future__ import annotations

import sys
import time
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from ral_ros_bridge.messages import Envelope
from ral_ros_bridge.node import BridgeNode, FakeNats, FakeRos


class BridgeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.nats = FakeNats()
        self.ros = FakeRos()
        self.node = BridgeNode("orbot-07", self.nats, self.ros, world_etag="118")
        self.node.start()

    def env(self, cycle: int, primitive: str, **payload) -> dict:
        return Envelope(
            event_id=f"e-{cycle}", robot_id="orbot-07", task_id="task-a", cycle_id=cycle,
            proposal_id=f"proposal-{cycle}", primitive_id=f"primitive-{cycle}", execution_id=f"exec-{cycle}",
            permit_id=f"permit-{cycle}", permit_expires_at=time.time()+60, schema="tti.motion_cmd.v2",
            payload={"primitive_type": primitive, **payload}, world_etag="118",
        ).to_dict()

    def test_focus_on_allowed_with_permit(self) -> None:
        self.nats.publish("ral.orbot-07.cmd.motion.head", self.env(1, "focus_on", frame="target"))
        self.assertEqual(self.ros.actions[-1][0], "/head_controller/follow_joint_trajectory")

    def test_missing_permit_fails_closed(self) -> None:
        msg = self.env(2, "nav_to_pose")
        msg["permit_id"] = None
        self.nats.publish("ral.orbot-07.cmd.motion.base", msg)
        self.assertTrue(any("permit provenance" in reason for reason in self.node.dropped))
        self.assertFalse(any(action[0] == "/navigate_to_pose" for action in self.ros.actions))

    def test_expired_permit_fails_closed(self) -> None:
        msg = self.env(3, "nav_to_pose")
        msg["permit_expires_at"] = time.time()-1
        self.nats.publish("ral.orbot-07.cmd.motion.base", msg)
        self.assertTrue(any("expired" in reason for reason in self.node.dropped))

    def test_stale_world_etag_fails_closed(self) -> None:
        msg = self.env(4, "nav_to_pose")
        msg["world_etag"] = "117"
        self.nats.publish("ral.orbot-07.cmd.motion.base", msg)
        self.assertIn("stale world_etag", self.node.dropped)

    def test_wrong_subject_fails_closed(self) -> None:
        self.nats.publish("ral.orbot-07.cmd.motion.head", self.env(5, "arm_follow"))
        self.assertTrue(any("subject/primitive mismatch" in reason for reason in self.node.dropped))

    def test_tool_and_proposal_are_not_subscribed(self) -> None:
        before = (len(self.ros.actions), len(self.ros.topics), len(self.ros.services))
        self.nats.publish("ral.orbot-07.cmd.tool.wipe", self.env(6, "wipe_ledger"))
        self.nats.publish("ral.orbot-07.cycle.6.proposal", self.env(6, "arm_follow"))
        after = (len(self.ros.actions), len(self.ros.topics), len(self.ros.services))
        self.assertEqual(before, after)

    def test_estop_does_not_wait_for_ordinary_permit(self) -> None:
        msg = Envelope(event_id="stop", robot_id="orbot-07", cycle_id="reflex-stop", schema="tti.estop.v1", priority="estop", payload={"primitive_type":"estop"}).to_dict()
        self.nats.publish("ral.orbot-07.cmd.estop", msg)
        self.assertEqual(self.ros.services[-1][0], "/emergency_stop")
        self.assertIn("/navigate_to_pose", self.ros.cancels)

    def test_joint_telemetry_is_rate_limited_and_effort_removed(self) -> None:
        self.assertTrue(self.node.on_joint_states({"name":["j1"],"position":[0.1],"effort":[9]}, now=10.0))
        self.assertFalse(self.node.on_joint_states({"name":["j1"],"position":[0.2],"effort":[10]}, now=10.005))
        rows=[payload for subject,payload in self.nats.published if subject.endswith("tel.motion.joints")]
        self.assertEqual(len(rows),1)
        self.assertNotIn("effort", rows[0]["payload"])

    def test_twist_latest_wins(self) -> None:
        first=self.env(10,"twist_base",linear=0.1)
        second=self.env(11,"twist_base",linear=0.2)
        self.nats.publish("ral.orbot-07.cmd.motion.base", first)
        # Force a recent emission so the next command becomes pending.
        self.node._last_twist_emit=time.monotonic()
        self.nats.publish("ral.orbot-07.cmd.motion.base", second)
        third=self.env(12,"twist_base",linear=0.3)
        self.nats.publish("ral.orbot-07.cmd.motion.base", third)
        self.node._last_twist_emit=0.0
        self.assertTrue(self.node.flush_twist())
        twists=[payload for topic,payload in self.ros.topics if topic=="/cmd_vel" and not payload.get("zero")]
        self.assertEqual(twists[-1]["linear"],0.3)

    def test_nats_disconnect_stops_base(self) -> None:
        self.node.on_nats_disconnect()
        self.assertIn("/navigate_to_pose", self.ros.cancels)
        self.assertTrue(any(topic=="/cmd_vel" and payload.get("zero") for topic,payload in self.ros.topics))


if __name__ == "__main__":
    unittest.main()
