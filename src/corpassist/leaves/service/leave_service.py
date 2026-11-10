from corpassist.core.enums import LeaveStatus
from corpassist.core.enums import LeaveType
from corpassist.leaves.schema.leave_schema import GetLeaveResponseSchema
from sqlalchemy import select
from corpassist.leaves.schema.leave_schema import CreateLeaveResponseSchema
from corpassist.leaves.schema.leave_schema import UpdateLeaveResponseSchema
from corpassist.leaves.schema.leave_schema import DeleteLeaveResponseSchema
import uuid
from corpassist.leaves.model.leave_model import LeaveModel
from corpassist.core.errors import IncompleteCredentialsError
from corpassist.leaves.schema.leave_schema import CreateLeaveRequestSchema
from corpassist.leaves.schema.leave_schema import UpdateLeaveRequestSchema
from sqlalchemy.ext.asyncio import AsyncSession


async def create_leave(
    db: AsyncSession,
    user_id: uuid.UUID,
    data: CreateLeaveRequestSchema
):
    try:
        if data.leave_type is None or data.start_date is None or data.end_date is None or data.days_count is None or data.reason is None:
            raise IncompleteCredentialsError

        leave_object = LeaveModel(
            user_id=user_id,
            leave_type=data.leave_type,
            start_date=data.start_date,
            end_date=data.end_date,
            days_count=data.days_count,
            reason=data.reason,
            status=LeaveStatus.PENDING
        )

        db.add(leave_object)
        await db.commit()
        await db.refresh(leave_object)

        return CreateLeaveResponseSchema(
            leave_id=leave_object.id,
            user_id=user_id,
            leave_type=data.leave_type,
            start_date=leave_object.start_date,
            end_date=leave_object.end_date,
            days_count=data.days_count,
            reason=data.reason,
            status=LeaveStatus.PENDING,
            created_at=leave_object.created_at,
            updated_at=leave_object.updated_at
        )

    except Exception:
        await db.rollback()
        raise



async def get_leave(
    db: AsyncSession,
    user_id: uuid.UUID,
    leave_id: uuid.UUID
):
    query = (
        select(LeaveModel)
        .where(LeaveModel.user_id == user_id, LeaveModel.id == leave_id)
    )

    result = await db.execute(query)

    leave_object = result.scalar_one_or_none()

    if leave_object is None:
        raise LookupError

    return GetLeaveResponseSchema(
        leave_id=leave_id,
        user_id=user_id,
        leave_type=leave_object.leave_type,
        start_date=leave_object.start_date,
        end_date=leave_object.end_date,
        days_count=leave_object.days_count,
        reason=leave_object.reason,
        status=leave_object.status,
        created_at=leave_object.created_at,
        updated_at=leave_object.updated_at
    )



async def list_leaves(
    db: AsyncSession,
    user_id: uuid.UUID,
    page_number: int = 1,
    page_size: int = 10,
    leave_type: LeaveType | None = None,
    status: LeaveStatus | None = None
):
    query = (
        select(LeaveModel)
        .where(LeaveModel.user_id == user_id)
    )

    if leave_type is not None:
        query = (
            query
            .where(LeaveModel.leave_type == leave_type)
        )

    if status is not None:
        query = (
            query
            .where(LeaveModel.status == status)
        )

    query = (
        query
        .order_by(LeaveModel.created_at.desc())
    )

    offset = (page_number - 1) * page_size

    query = (
        query
        .offset(offset)
        .limit(page_size)
    )

    result = await db.execute(query)

    leaves = result.scalars().all()

    return leaves



async def update_leave(
    db: AsyncSession,
    user_id: uuid.UUID,
    leave_id: uuid.UUID,
    data: UpdateLeaveRequestSchema
):
    try:
        query = (
            select(LeaveModel)
            .where(LeaveModel.user_id == user_id, LeaveModel.id == leave_id)
        )

        result = await db.execute(query)

        leave_object = result.scalar_one_or_none()

        if leave_object is None:
            raise LookupError

        updates = data.model_dump(exclude_unset=True)

        if not updates:
            raise IncompleteCredentialsError

        for field, value in updates.items():
            setattr(leave_object, field, value)

        await db.commit()
        await db.refresh(leave_object)

        return UpdateLeaveResponseSchema(
            leave_id=leave_object.id,
            user_id=user_id,
            leave_type=leave_object.leave_type,
            start_date=leave_object.start_date,
            end_date=leave_object.end_date,
            days_count=leave_object.days_count,
            reason=leave_object.reason,
            status=leave_object.status,
            created_at=leave_object.created_at,
            updated_at=leave_object.updated_at
        )

    except Exception:
        await db.rollback()
        raise



async def delete_leave(
    db: AsyncSession,
    user_id: uuid.UUID,
    leave_id: uuid.UUID
):
    try:
        query = (
            select(LeaveModel)
            .where(LeaveModel.user_id == user_id, LeaveModel.id == leave_id)
        )

        result = await db.execute(query)

        leave_object = result.scalar_one_or_none()

        if leave_object is None:
            raise LookupError

        await db.delete(leave_object)
        await db.commit()

        return DeleteLeaveResponseSchema(
            leave_id=leave_id,
            message="Leave request deleted successfully"
        )

    except Exception:
        await db.rollback()
        raise
