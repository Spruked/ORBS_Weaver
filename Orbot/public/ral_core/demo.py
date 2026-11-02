from __future__ import annotations

import asyncio
from .event_bus import AsyncExecutionFabric
from .middleware import TTIValidationMiddleware
from .models import ActionProposal, ExecutionPrimitive, WorldState, utc_now_iso


async def _handler(primitive: ExecutionPrimitive):
    await asyncio.sleep(0.001)
    return {"capability": primitive.capability, "ok": True}


async def main() -> None:
    world = WorldState(
        snapshot_id="ws-1",
        version=7,
        captured_at=utc_now_iso(),
        authority="action",
        components=["status_panel"],
    )
    proposal = ActionProposal(
        proposal_id="proposal-1",
        cycle_id="42",
        world_state_snapshot_id=world.snapshot_id,
        world_state_version=world.version,
        task="guide to status panel",
        intent="guide",
        required_authority="guidance",
        primitives=[
            ExecutionPrimitive(
                primitive_id="motion-1",
                lane="motion",
                capability="focus_on",
                arguments={"target_pointer": "component:status_panel"},
                required_authority="guidance",
            )
        ],
    )
    fabric = AsyncExecutionFabric()
    fabric.register_handler("motion", _handler)
    middleware = TTIValidationMiddleware(fabric)
    result = await middleware.intercept_and_dispatch(proposal, world)
    assert result["status"] == "PERMITTED"
    permit = result["permit"]
    assert permit.permit_id
    assert permit.world_etag == world.etag
    await fabric.run_one("motion")
    assert fabric.telemetry[-1].status == "COMPLETED"
    print("ral_core demo: permit path passed")


if __name__ == "__main__":
    asyncio.run(main())
