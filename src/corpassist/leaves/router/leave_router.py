from corpassist.leaves.service.leave_service import list_leaves
from corpassist.core.enums import LeaveStatus
from corpassist.core.enums import LeaveType
from fastapi import Query
import uuid
from corpassist.leaves.service.leave_service import get_leave
from fastapi import status
from fastapi import HTTPException
from corpassist.core.errors import IncompleteCredentialsError
from corpassist.leaves.service.leave_service import create_leave
from corpassist.auth.utils.current_user_utils import get_user
from corpassist.auth.model.user_model import UserModel
from corpassist.core.db import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from corpassist.leaves.schema.leave_schema import CreateLeaveRequestSchema
from corpassist.leaves.schema.leave_schema import UpdateLeaveRequestSchema
from corpassist.leaves.service.leave_service import update_leave
from corpassist.leaves.service.leave_service import delete_leave
from fastapi import APIRouter


leave_router = APIRouter(tags=["LEAVE"])



@leave_router.post("/leave")
async def execute_create_leave(
    data: CreateLeaveRequestSchema,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_user)
):
    try:
        result = await create_leave(
            user_id=user.id,
            data=data,
            db=db
        )

        return result

    except IncompleteCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad input"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



@leave_router.get("/leave/{leave_id}")
async def execute_get_leave(
    leave_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_user)
):
    try:
        result = await get_leave(
            db=db,
            user_id=user.id,
            leave_id=leave_id
        )

        return result

    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



@leave_router.get("/leave")
async def execute_list_leaves(
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_user),
    page_number: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, le=100),
    leave_type: LeaveType | None = None,
    status: LeaveStatus | None = None
):
    try:
        result = await list_leaves(
            db=db,
            user_id=user.id,
            page_number=page_number,
            page_size=page_size,
            leave_type=leave_type,
            status=status
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



@leave_router.put("/leave/{leave_id}")
async def execute_update_leave(
    leave_id: uuid.UUID,
    data: UpdateLeaveRequestSchema,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_user)
):
    try:
        result = await update_leave(
            db=db,
            user_id=user.id,
            leave_id=leave_id,
            data=data
        )

        return result

    except IncompleteCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad input"
        )

    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



@leave_router.delete("/leave/{leave_id}")
async def execute_delete_leave(
    leave_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_user)
):
    try:
        result = await delete_leave(
            db=db,
            user_id=user.id,
            leave_id=leave_id
        )

        return result

    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
