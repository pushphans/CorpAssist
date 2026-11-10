from datetime import datetime
import uuid
from corpassist.core.enums import TicketPriority
from corpassist.core.enums import TicketStatus
from pydantic import Field
from pydantic import BaseModel


class CreateTicketRequestSchema(BaseModel):
    title : str = Field(..., min_length=10, max_length=50)
    description : str = Field(..., min_length=10, max_length=250)
    status : TicketStatus = Field(default=TicketStatus.OPEN)
    priority : TicketPriority = Field(default=TicketPriority.MEDIUM)


class CreateTicketResponseSchema(BaseModel):
    ticket_id : uuid.UUID
    user_id : uuid.UUID
    title : str
    description : str
    status : TicketStatus
    priority : TicketPriority
    created_at : datetime
    updated_at : datetime



class GetTicketResponseSchema(BaseModel):
    ticket_id : uuid.UUID
    user_id : uuid.UUID
    title : str
    description : str
    status : TicketStatus
    priority : TicketPriority
    created_at : datetime
    updated_at : datetime



class UpdateTicketRequestSchema(BaseModel):
    title : str = Field(..., max_length=50, min_length=10)
    description : str = Field(..., min_length=10, max_length=250)
    status : TicketStatus
    priority : TicketPriority



class UpdateTicketResponseSchema(BaseModel):
    ticket_id : uuid.UUID
    user_id : uuid.UUID
    title : str
    description : str
    status : TicketStatus
    priority : TicketPriority
    created_at : datetime
    updated_at : datetime