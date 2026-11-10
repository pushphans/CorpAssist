import json
import uuid
from typing import Annotated

from langchain_core.tools import BaseTool, tool
from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession

from corpassist.core.enums import TicketPriority, TicketStatus
from corpassist.tickets.schema.ticket_schema import CreateTicketRequestSchema
from corpassist.tickets.service.ticket_service import create_ticket, list_tickets


def ticket_tools(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> list[BaseTool]:
    @tool
    async def search_tickets(
        status: Annotated[TicketStatus | None, Field(description="Filter by ticket status")] = None,
        priority: Annotated[TicketPriority | None, Field(description="Filter by ticket priority")] = None,
    ) -> str:
        """Search the user's support tickets, optionally filtered by status or priority. Returns a JSON list of matching tickets."""
        tickets = await list_tickets(
            db,
            user_id,
            page_number=1,
            page_size=10,
            priority=priority,
            status=status,
        )

        return json.dumps(
            [
                {
                    "ticket_id": str(ticket.id),
                    "title": ticket.title,
                    "description": ticket.description,
                    "status": ticket.status.value,
                    "priority": ticket.priority.value,
                }
                for ticket in tickets
            ],
            indent=2,
        )


    @tool
    async def create_new_ticket(
        title: Annotated[str, Field(description="Short title for the ticket", min_length=10, max_length=50)],
        description: Annotated[str, Field(description="Detailed description of the issue", min_length=10, max_length=250)],
        priority: Annotated[TicketPriority, Field(description="Priority of the ticket")] = TicketPriority.MEDIUM,
    ) -> str:
        """Create a new support ticket for the user. Returns the created ticket details as JSON."""
        ticket = await create_ticket(
            db,
            user_id,
            CreateTicketRequestSchema(title=title, description=description, priority=priority),
        )

        return json.dumps(
            {
                "ticket_id": str(ticket.ticket_id),
                "title": ticket.title,
                "description": ticket.description,
                "status": ticket.status.value,
                "priority": ticket.priority.value,
            },
            indent=2,
        )


    return [search_tickets, create_new_ticket]
