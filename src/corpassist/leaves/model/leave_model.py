from datetime import datetime
from datetime import date
from corpassist.core.enums import LeaveStatus
from corpassist.core.enums import LeaveType
from sqlalchemy import ForeignKey
import uuid
from corpassist.core.db import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Text, Boolean, func, DateTime, UUID, Date, Integer
from sqlalchemy import Enum as SQLEnum



class LeaveModel(Base):
    __tablename__ = "leave_balance"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    leave_type: Mapped[LeaveType] = mapped_column(SQLEnum(LeaveType), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    days_count: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[LeaveStatus] = mapped_column( SQLEnum(LeaveStatus), default=LeaveStatus.PENDING, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate = func.now(), nullable=False)
