from corpassist.core.enums import TicketStatus
from corpassist.core.enums import TicketPriority
from corpassist.tickets.schema.ticket_schema import GetTicketResponseSchema
from sqlalchemy import select
from corpassist.tickets.schema.ticket_schema import CreateTicketResponseSchema
import uuid
from corpassist.tickets.model.ticket_model import TicketModel
from corpassist.core.errors import IncompleteCredentialsError
from corpassist.tickets.schema.ticket_schema import CreateTicketRequestSchema
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Query



async def create_ticket(
    db : AsyncSession,
    user_id : uuid.UUID,
    data : CreateTicketRequestSchema
):
    try:
        if data.title is None or data.description is None or data.status is None or data.priority is None:
            raise IncompleteCredentialsError


        ticket_object = TicketModel(
            user_id = user_id,
            title = data.title,
            description = data.description,
            status = data.status,
            priority = data.priority
        )

        db.add(ticket_object)
        await db.commit()
        await db.refresh(ticket_object)

        return CreateTicketResponseSchema(
            ticket_id=ticket_object.id,
            user_id=user_id,
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            created_at=ticket_object.created_at,
            updated_at=ticket_object.updated_at
        )

    except Exception:
        await db.rollback()
        raise 



async def get_ticket(
    db : AsyncSession,
    user_id : uuid.UUID,
    ticket_id : uuid.UUID
):
    query = (
        select(TicketModel)
        .where(TicketModel.user_id == user_id, TicketModel.id == ticket_id)
    )


    result = await db.execute(query)

    ticket_object = result.scalar_one_or_none()

    if ticket_object is None:
        raise LookupError

    return GetTicketResponseSchema(
        ticket_id=ticket_id,
        user_id=user_id,
        title=ticket_object.title,
        description=ticket_object.description,
        status=ticket_object.status,
        priority=ticket_object.priority,
        created_at=ticket_object.created_at,
        updated_at=ticket_object.updated_at
    )



async def list_tickets(
    db : AsyncSession,
    user_id : uuid.UUID,
    page_number : int = Query(default=1, ge=1),
    page_size : int = Query(default = 10, le = 100),
    priority : TicketPriority | None = None,
    status : TicketStatus | None = None
):
    query = (
            select(TicketModel)
            .where(TicketModel.user_id == user_id)
        )

    if not priority is None:
        query = (
            query
            .where(TicketModel.priority == priority)
            )


    if not status is None:
        query = (
            query
            .where(TicketModel.status == status)
            )


    offset = (page_number - 1) * page_size

    query = (
        query
        .offset(offset)
        .limit(page_size)
        )


    result = await db.execute(query)

    tickets = result.scalars().all()


    return tickets


    