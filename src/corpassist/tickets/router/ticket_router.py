from corpassist.tickets.service.ticket_service import delete_ticket
from corpassist.tickets.service.ticket_service import update_ticket
from corpassist.tickets.schema.ticket_schema import UpdateTicketRequestSchema
from corpassist.tickets.service.ticket_service import list_tickets
from corpassist.core.enums import TicketStatus
from corpassist.core.enums import TicketPriority
from fastapi import Query
import uuid
from corpassist.tickets.service.ticket_service import get_ticket
from fastapi import status
from fastapi import HTTPException
from corpassist.core.errors import IncompleteCredentialsError
from corpassist.tickets.service.ticket_service import create_ticket
from corpassist.auth.utils.current_user_utils import get_user
from corpassist.auth.model.user_model import UserModel
from corpassist.core.db import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from corpassist.tickets.schema.ticket_schema import CreateTicketRequestSchema
from fastapi import APIRouter

ticket_router = APIRouter(tags=["TICKET"])



@ticket_router.post("/ticket")
async def execute_create_ticket(
    data : CreateTicketRequestSchema,
    db : AsyncSession = Depends(get_db),
    user : UserModel = Depends(get_user)
):
    try:
        result = await create_ticket(
            user_id=user.id,
            data=data,
            db=db
        )

        return  result

    except IncompleteCredentialsError:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Bad input"
        )

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        )



@ticket_router.get("/ticket/{ticket_id}")
async def execute_get_ticket(
    ticket_id : uuid.UUID,
    db : AsyncSession = Depends(get_db),
    user : UserModel = Depends(get_user)
):
    try:
        result = await get_ticket(
            db = db,
            user_id=user.id,
            ticket_id=ticket_id
        )

        return result

    except LookupError:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Not found"
        )


    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        )




@ticket_router.get("/ticket")
async def execute_list_tickets(
    db : AsyncSession = Depends(get_db),
    user : UserModel = Depends(get_user),
    page_number : int = Query(default=1, ge=1),
    page_size : int = Query(default = 10, le = 100),
    priority : TicketPriority | None = None,
    status : TicketStatus | None = None
):
    try:
        result = await list_tickets(
            db = db,
            user_id=user.id,
            page_number=page_number,
            page_size=page_size,
            priority=priority,
            status = status

        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        )




@ticket_router.put("/ticket/{ticket_id}")
async def execute_update_ticket(
    ticket_id : uuid.UUID,
    data : UpdateTicketRequestSchema,
    db : AsyncSession = Depends(get_db),
    user : UserModel = Depends(get_user)
):
    try:
        result = await update_ticket(
            ticket_id=ticket_id,
            data=data,
            db=db, 
            user_id=user.id
        )


        return result

    except LookupError:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Not found"
        )


    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        )




@ticket_router.delete("/ticket/{ticket_id}")
async def execute_delete_ticket(
    ticket_id : uuid.UUID,
    db : AsyncSession = Depends(get_db),
    user : UserModel = Depends(get_user)
):
    try:
        result = await delete_ticket(
            ticket_id=ticket_id,
            db=db, 
            user_id=user.id
        )

        return result

    except LookupError:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Not found"
        )


    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        )