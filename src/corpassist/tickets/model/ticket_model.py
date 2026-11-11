from corpassist.core.enums import TicketPriority
from corpassist.core.enums import TicketStatus
from datetime import datetime
from sqlalchemy import Text, func, UUID, DateTime
from sqlalchemy import ForeignKey
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from corpassist.core.db import Base
from sqlalchemy import Enum as SQLEnum



class TicketModel(Base):
    __tablename__ = "tickets"

    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key = True, default = uuid.uuid4, nullable = False)
    user_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index = True, nullable = False)
    title : Mapped[str] = mapped_column(Text, nullable = False)
    description : Mapped[str] = mapped_column(Text)
    status : Mapped[TicketStatus] = mapped_column(SQLEnum(TicketStatus), nullable = False, default = TicketStatus.OPEN)
    priority : Mapped[TicketPriority] = mapped_column(SQLEnum(TicketPriority), nullable = False, default = TicketPriority.MEDIUM)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default = func.now(), nullable = False)
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default = func.now(), onupdate = func.now(), nullable = False)