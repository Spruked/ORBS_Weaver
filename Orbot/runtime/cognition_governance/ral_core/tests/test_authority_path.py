import asyncio
import unittest
from datetime import datetime, timezone

from ral_core.admission import AdmissionRejected, HardAdmissionGate
from ral_core.core4 import evaluate_core4
from ral_core.event_bus import AsyncExecutionFabric
from ral_core.middleware import TTIValidationMiddleware
from ral_core.models import ActionProposal, ExecutionPrimitive, WorldState


class AuthorityPathTests(unittest.TestCase):
    def world(self, **changes):
        base = dict(
            snapshot_id="ws-1",
            version=4,
            captured_at=datetime.now(timezone.utc).isoformat(),
            authority="action",
            components=["panel"],
            forbidden_regions=["system:kernel"],
        )
        base.update(changes)
        return WorldState(**base)

    def proposal(self, world, **changes):
        base = dict(
            proposal_id="p-1",
            cycle_id="c-1",
            world_state_snapshot_id=world.snapshot_id,
            world_state_version=world.version,
            task="guide user",
            intent="guide",
            required_authority="guidance",
            primitives=[ExecutionPrimitive(
                primitive_id="m-1",
                lane="motion",
                capability="focus_on",
                arguments={"target_pointer": "component:panel"},
                required_authority="guidance",
            )],
            confidence=0.9,
        )
        base.update(changes)
        return ActionProposal(**base)

    def test_core4_allow_is_not_itself_a_permit(self):
        world = self.world()
        proposal = self.proposal(world)
        evaluation = evaluate_core4(proposal, world)
        self.assertEqual(evaluation.disposition, "ADMISSIBLE")
        self.assertFalse(hasattr(evaluation, "permit_id"))

    def test_hard_admission_issues_permit(self):
        world = self.world()
        proposal = self.proposal(world)
        evaluation = evaluate_core4(proposal, world)
        permit = HardAdmissionGate().admit(proposal, world, evaluation)
        self.assertTrue(permit.permit_id.startswith("permit-"))
        self.assertEqual(permit.world_etag, world.etag)
        self.assertEqual(permit.approved_primitive_ids, ["m-1"])

    def test_stale_world_replans(self):
        world = self.world()
        proposal = self.proposal(world, world_state_version=3)
        evaluation = evaluate_core4(proposal, world)
        self.assertEqual(evaluation.disposition, "REPLAN")

    def test_insufficient_authority_rejects(self):
        world = self.world(authority="guidance")
        proposal = self.proposal(world, required_authority="action")
        evaluation = evaluate_core4(proposal, world)
        self.assertEqual(evaluation.disposition, "REJECTED")

    def test_high_risk_without_confirmation_defers(self):
        world = self.world()
        proposal = self.proposal(world, risk_profile="high", user_confirmed=False)
        evaluation = evaluate_core4(proposal, world)
        self.assertEqual(evaluation.disposition, "DEFERRED")

    def test_forbidden_target_replans(self):
        world = self.world()
        primitive = ExecutionPrimitive(
            primitive_id="m-1", lane="motion", capability="focus_on",
            arguments={"target_pointer": "system:kernel"}, required_authority="guidance"
        )
        proposal = self.proposal(world, primitives=[primitive])
        evaluation = evaluate_core4(proposal, world)
        self.assertEqual(evaluation.disposition, "REPLAN")

    def test_dispatch_enqueues_without_waiting_for_handler(self):
        async def scenario():
            world = self.world()
            proposal = self.proposal(world)
            fabric = AsyncExecutionFabric()
            started = asyncio.Event()
            release = asyncio.Event()
            async def handler(_):
                started.set()
                await release.wait()
                return {"ok": True}
            fabric.register_handler("motion", handler)
            middleware = TTIValidationMiddleware(fabric)
            result = await middleware.intercept_and_dispatch(proposal, world)
            self.assertEqual(result["status"], "PERMITTED")
            self.assertFalse(started.is_set())
            run = asyncio.create_task(fabric.run_one("motion"))
            await started.wait()
            self.assertFalse(run.done())
            release.set()
            await run
            self.assertEqual(fabric.telemetry[-1].status, "COMPLETED")
        asyncio.run(scenario())

    def test_cancel_group_prevents_execution(self):
        async def scenario():
            world = self.world()
            primitive = ExecutionPrimitive(
                primitive_id="m-1", lane="motion", capability="focus_on",
                arguments={"target_pointer": "component:panel"}, cancel_group="task-1"
            )
            proposal = self.proposal(world, primitives=[primitive])
            fabric = AsyncExecutionFabric()
            called = False
            async def handler(_):
                nonlocal called
                called = True
                return {}
            fabric.register_handler("motion", handler)
            result = await TTIValidationMiddleware(fabric).intercept_and_dispatch(proposal, world)
            self.assertEqual(result["status"], "PERMITTED")
            fabric.cancel_group("task-1")
            event = await fabric.run_one("motion")
            self.assertEqual(event.status, "CANCELLED")
            self.assertFalse(called)
        asyncio.run(scenario())


if __name__ == "__main__":
    unittest.main()
