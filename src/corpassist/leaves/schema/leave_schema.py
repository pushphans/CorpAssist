from datetime import datetime, date
import uuid
from corpassist.core.enums import LeaveStatus
from corpassist.core.enums import LeaveType
from pydantic import BaseModel
from pydantic import Field


class CreateLeaveRequestSchema(BaseModel):
    leave_type: LeaveType
    start_date: date
    end_date: date
    days_count: int = Field(..., ge=1)
    reason: str = Field(..., min_length=1)


class CreateLeaveResponseSchema(BaseModel):
    leave_id: uuid.UUID
    user_id: uuid.UUID
    leave_type: LeaveType
    start_date: date
    end_date: date
    days_count: int
    reason: str
    status: LeaveStatus
    created_at: datetime
    updated_at: datetime


class GetLeaveResponseSchema(BaseModel):
    leave_id: uuid.UUID
    user_id: uuid.UUID
    leave_type: LeaveType
    start_date: date
    end_date: date
    days_count: int
    reason: str
    status: LeaveStatus
    created_at: datetime
    updated_at: datetime


class UpdateLeaveRequestSchema(BaseModel):
    leave_type: LeaveType | None = None
    start_date: date | None = None
    end_date: date | None = None
    days_count: int | None = Field(default=None, ge=1)
    reason: str | None = Field(default=None, min_length=1)
    status: LeaveStatus | None = None


class UpdateLeaveResponseSchema(BaseModel):
    leave_id: uuid.UUID
    user_id: uuid.UUID
    leave_type: LeaveType
    start_date: date
    end_date: date
    days_count: int
    reason: str
    status: LeaveStatus
    created_at: datetime
    updated_at: datetime


class DeleteLeaveResponseSchema(BaseModel):
    leave_id: uuid.UUID
    message: str
