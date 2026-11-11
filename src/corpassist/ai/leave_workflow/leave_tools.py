from datetime import date
from typing import Annotated
from uuid import UUID

from langchain.tools import tool
from langgraph.prebuilt import ToolRuntime
from pydantic import Field

from corpassist.ai.core.llm_utils import AiContext
from corpassist.core.db import session_factory
from corpassist.core.enums import LeaveStatus, LeaveType
from corpassist.leaves.schema.leave_schema import (
    CreateLeaveRequestSchema,
    GetLeaveResponseSchema,
    UpdateLeaveRequestSchema,
)
from corpassist.leaves.service.leave_service import (
    create_leave,
    delete_leave,
    get_leave,
    list_leaves,
    update_leave,
)


@tool
async def create_leave_tool(
    runtime: ToolRuntime[AiContext],
    leave_type: LeaveType,
    start_date: date,
    end_date: date,
    days_count: Annotated[int, Field(ge=1)],
    reason: Annotated[str, Field(min_length=1)],
) -> dict:
    """Create a leave request for the authenticated user with PENDING status.

    Provide dates in YYYY-MM-DD format, a positive days count, and a reason.
    Leave type can be CASUAL, SICK, or EARNED.
    """
    data = CreateLeaveRequestSchema(
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        days_count=days_count,
        reason=reason,
    )

    async with session_factory() as db:
        result = await create_leave(
            db=db,
            user_id=runtime.context.user_id,
            data=data,
        )
        return result.model_dump(mode="json")


@tool
async def get_leave_tool(
    runtime: ToolRuntime[AiContext],
    leave_id: UUID,
) -> dict:
    """Get the authenticated user's leave request using its leave UUID."""
    async with session_factory() as db:
        result = await get_leave(
            db=db,
            user_id=runtime.context.user_id,
            leave_id=leave_id,
        )
        return result.model_dump(mode="json")


@tool
async def list_leaves_tool(
    runtime: ToolRuntime[AiContext],
    page_number: Annotated[int, Field(ge=1)] = 1,
    page_size: Annotated[int, Field(ge=1, le=100)] = 10,
    leave_type: LeaveType | None = None,
    status: LeaveStatus | None = None,
) -> list[dict]:
    """List the authenticated user's leave requests with optional type/status filters.

    Pages start at 1 and contain 10 requests by default, with at most 100
    requests per page. An empty list means no requests matched on that page.
    """
    async with session_factory() as db:
        leaves = await list_leaves(
            db=db,
            user_id=runtime.context.user_id,
            page_number=page_number,
            page_size=page_size,
            leave_type=leave_type,
            status=status,
        )
        return [
            GetLeaveResponseSchema(
                leave_id=leave.id,
                user_id=leave.user_id,
                leave_type=leave.leave_type,
                start_date=leave.start_date,
                end_date=leave.end_date,
                days_count=leave.days_count,
                reason=leave.reason,
                status=leave.status,
                created_at=leave.created_at,
                updated_at=leave.updated_at,
            ).model_dump(mode="json")
            for leave in leaves
        ]


@tool
async def update_leave_tool(
    runtime: ToolRuntime[AiContext],
    leave_id: UUID,
    leave_type: LeaveType | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    days_count: Annotated[int | None, Field(ge=1)] = None,
    reason: Annotated[str | None, Field(min_length=1)] = None,
    status: LeaveStatus | None = None,
) -> dict:
    """Update the authenticated user's leave request using its leave UUID.

    Supply at least one field to change. Omitted or null fields are left
    unchanged. Dates use YYYY-MM-DD format.
    """
    updates = {
        key: value
        for key, value in {
            "leave_type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "days_count": days_count,
            "reason": reason,
            "status": status,
        }.items()
        if value is not None
    }
    if not updates:
        raise ValueError("Provide at least one field to update.")

    data = UpdateLeaveRequestSchema(**updates)
    async with session_factory() as db:
        result = await update_leave(
            db=db,
            user_id=runtime.context.user_id,
            leave_id=leave_id,
            data=data,
        )
        return result.model_dump(mode="json")


@tool
async def delete_leave_tool(
    runtime: ToolRuntime[AiContext],
    leave_id: UUID,
) -> dict:
    """Permanently delete the authenticated user's leave request by UUID.

    Use only when the user explicitly requests deletion of that leave request.
    """
    async with session_factory() as db:
        result = await delete_leave(
            db=db,
            user_id=runtime.context.user_id,
            leave_id=leave_id,
        )
        return result.model_dump(mode="json")


leave_tools = [
    create_leave_tool,
    get_leave_tool,
    list_leaves_tool,
    update_leave_tool,
    delete_leave_tool,
]
