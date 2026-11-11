from corpassist.tickets.service.ticket_service import get_ticket
import uuid
from typing import Annotated

from pydantic import Field
from corpassist.ai.core.llm_utils import AiContext
from langgraph.prebuilt import ToolRuntime
from corpassist.core.db import session_factory
from corpassist.tickets.schema.ticket_schema import CreateTicketRequestSchema
from corpassist.tickets.schema.ticket_schema import GetTicketResponseSchema
from corpassist.tickets.service.ticket_service import create_ticket
from corpassist.tickets.service.ticket_service import list_tickets
from corpassist.core.enums import TicketPriority
from corpassist.core.enums import TicketStatus
from langchain.tools import tool


@tool
async def create_ticket_tool(
    runtime : ToolRuntime[AiContext],
    title : str,
    description : str, 
    status : TicketStatus = TicketStatus.OPEN,
    priority : TicketPriority = TicketPriority.MEDIUM,
) -> dict:

    """Create a support ticket for the authenticated user.

    Provide a title of 10-50 characters and a description of 10-250
    characters. Status defaults to OPEN and priority defaults to MEDIUM.
    """

    data = CreateTicketRequestSchema(
        title=title,
        description=description,
        status=status, 
        priority=priority
    )

    async with session_factory() as db:
        result = await create_ticket(
            data=data,
            db=db,
            user_id=runtime.context.user_id
        )


        return result.model_dump(mode="json")




@tool
async def get_ticket_tool(
    runtime : ToolRuntime[AiContext],
    ticket_id : uuid.UUID
) -> dict:

    """Get the authenticated user's ticket using its ticket UUID."""

    async with session_factory() as db:
        result = await get_ticket(
            ticket_id=ticket_id,
            db=db,
            user_id=runtime.context.user_id
        )


        return result.model_dump(mode="json")


@tool
async def list_tickets_tool(
    runtime: ToolRuntime[AiContext],
    page_number: Annotated[int, Field(ge=1)] = 1,
    page_size: Annotated[int, Field(ge=1, le=100)] = 10,
    priority: TicketPriority | None = None,
    status: TicketStatus | None = None,
) -> list[dict]:
    """List the authenticated user's tickets with optional priority/status filters.

    Pages start at 1 and contain 10 tickets by default, with at most 100
    tickets per page. An empty list means no tickets matched on that page.
    """
    async with session_factory() as db:
        tickets = await list_tickets(
            db=db,
            user_id=runtime.context.user_id,
            page_number=page_number,
            page_size=page_size,
            priority=priority,
            status=status,
        )

        return [
            GetTicketResponseSchema(
                ticket_id=ticket.id,
                user_id=ticket.user_id,
                title=ticket.title,
                description=ticket.description,
                status=ticket.status,
                priority=ticket.priority,
                created_at=ticket.created_at,
                updated_at=ticket.updated_at,
            ).model_dump(mode="json")

            for ticket in tickets
        ]


ticket_tools = [create_ticket_tool, get_ticket_tool, list_tickets_tool]