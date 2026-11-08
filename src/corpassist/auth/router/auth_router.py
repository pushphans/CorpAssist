from corpassist.core.errors import RefreshTokenExpired
from corpassist.auth.utils.current_user_utils import InvalidCredentialError
from corpassist.core.errors import UserAlreadyExistsError
from corpassist.core.errors import IncompleteCredentialsError
from corpassist.auth.services.auth_service import refresh_token
from corpassist.auth.schema.auth_schemas import RefreshTokenRequestModel
from corpassist.auth.services.auth_service import login
from corpassist.auth.schema.auth_schemas import LoginRequestModel
from corpassist.auth.services.auth_service import register
from fastapi import status
from fastapi import HTTPException
from corpassist.auth.schema.auth_schemas import RegisterRequestModel
from corpassist.auth.utils.current_user_utils import get_user
from corpassist.auth.model.user_model import UserModel
from corpassist.core.db import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter


auth_router = APIRouter(prefix="/auth", tags = ["AUTH"])



@auth_router.post("/register")
async def execute_register(
    data : RegisterRequestModel,
    db : AsyncSession = Depends(get_db),
):
    try:
        result = await register(data=data, db=db)
        return result

    except IncompleteCredentialsError:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Invalid input"
        )

    except UserAlreadyExistsError:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "User already exists"
        )

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        )




@auth_router.post("/login")
async def execute_login(
    data : LoginRequestModel,
    db : AsyncSession = Depends(get_db),
):
    try:
        result = await login(data=data, db=db)
        return result

    except IncompleteCredentialsError:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Invalid input"
        )


    except InvalidCredentialError:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Invalid credentials"
        )

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        )


@auth_router.post("/refresh-token")
async def execute_refresh_token(
    data : RefreshTokenRequestModel,
    db : AsyncSession = Depends(get_db),
):
    try:
        result = await refresh_token(db=db, data=data)
        return result

    except LookupError:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "No token found"
        )

    except RefreshTokenExpired:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Refresh token expired, login again"
        )

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        )
