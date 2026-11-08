from corpassist.core.errors import RefreshTokenExpired
from corpassist.auth.utils.current_user_utils import InvalidCredentialError
from corpassist.core.errors import UserAlreadyExistsError
from corpassist.core.errors import IncompleteCredentialsError
from corpassist.auth.schema.auth_schemas import RefreshTokenResponseModel
from corpassist.auth.schema.auth_schemas import RefreshTokenRequestModel
from corpassist.auth.schema.auth_schemas import LoginResponseModel
from datetime import timedelta
from datetime import timezone
from datetime import datetime
from corpassist.auth.utils.jwt_utils import create_refresh_token
from corpassist.auth.model.refresh_token_model import RefreshTokenModel
from corpassist.core.config import settings
from corpassist.auth.utils.jwt_utils import create_access_token
from corpassist.auth.utils.password_utils import verify_password
from corpassist.auth.schema.auth_schemas import RegisterResponseModel
from corpassist.auth.utils.password_utils import hash_password
from corpassist.auth.model.user_model import UserModel
from sqlalchemy import select
from corpassist.auth.schema.auth_schemas import RegisterRequestModel
from corpassist.auth.schema.auth_schemas import LoginRequestModel
from sqlalchemy.ext.asyncio import AsyncSession






async def register(
    db : AsyncSession,
    data : RegisterRequestModel
):
    try:
        if data.email is None:
            raise IncompleteCredentialsError

        if data.password is None:
            raise IncompleteCredentialsError

        query = (
            select(UserModel)
            .where(UserModel.email == data.email)
        )

        result = await db.execute(query)

        user = result.scalar_one_or_none()

        if user:
            raise UserAlreadyExistsError

        user = UserModel(
            name = data.name,
            email = data.email,
            password_hash = await hash_password(password=data.password)
        )

        db.add(user)

        await db.commit()
        await db.refresh(user)

        return RegisterResponseModel(
            user_id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    except Exception:
        await db.rollback()
        raise


async def login(
    db : AsyncSession,
    data : LoginRequestModel
):
    try:
        if data.email is None:
            raise IncompleteCredentialsError

        if data.password is None:
            raise IncompleteCredentialsError

        query = (
            select(UserModel)
            .where(UserModel.email == data.email)
        )

        result = await db.execute(query)

        user = result.scalar_one_or_none()

        if user is None:
            raise LookupError

        password_verified = verify_password(password=data.password, hashed_password=user.password_hash)

        if not password_verified:
            raise InvalidCredentialError

        new_access_token = await create_access_token(user_id=user.id)
        new_access_token_expiry = settings.ACCESS_TOKEN_EXPIRY_IN_MINUTES * 60

        new_refresh_token = await create_refresh_token()
        new_refresh_token_expiry = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRY_IN_DAYS)

        refresh_token_query = (
            select(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user.id)
        )

        rt_result = await db.execute(refresh_token_query)

        rt_object = rt_result.scalar_one_or_none()

        if rt_object is None:
            rt_object = RefreshTokenModel(
                refresh_token = new_refresh_token,
                refresh_token_expiry = new_refresh_token_expiry
            )

            db.add(rt_object)


        rt_object.refresh_token = new_refresh_token
        rt_object.refresh_token_expiry = new_refresh_token_expiry

        await db.commit()
        await db.refresh(rt_object)

        return LoginResponseModel(
            user_id=user.id,
            name=user.name,
            email=user.email,
            access_token=new_access_token,
            access_token_expiry=new_access_token_expiry,
            refresh_token=rt_object.refresh_token,
            created_at=user.created_at,
            updated_at=user.updated_at
        )


    except Exception:
        await db.rollback()
        raise




async def refresh_token(
    db : AsyncSession,
    data : RefreshTokenRequestModel
):
    try:
        query = (
            select(RefreshTokenModel)
            .where(RefreshTokenModel.refresh_token == data.refresh_token)
        )

        result = await db.execute(query)

        rt_exist = result.scalar_one_or_none()

        if rt_exist is None:
            raise LookupError

        if rt_exist.refresh_token_expiry < datetime.now(timezone.utc):
            # await db.delete(rt_exist)
            raise RefreshTokenExpired


        new_access_token = await create_access_token(user_id=rt_exist.user_id)
        new_access_token_expiry = settings.ACCESS_TOKEN_EXPIRY_IN_MINUTES * 60

        new_refresh_token = await create_refresh_token()
        new_refresh_token_expiry = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRY_IN_DAYS)

        rt_exist.refresh_token = new_refresh_token
        rt_exist.refresh_token_expiry = new_refresh_token_expiry

        await db.commit()

        return RefreshTokenResponseModel(
            refresh_token=new_refresh_token,
            access_token=new_access_token,
            access_token_expiry=new_access_token_expiry
        )
    
    except Exception:
        await db.rollback()
        raise