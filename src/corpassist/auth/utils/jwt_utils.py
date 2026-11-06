from corpassist.core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import secrets
import jwt
from corpassist.core.config import settings
from datetime import timedelta
from datetime import timezone
from datetime import datetime
import uuid
from fastapi import Depends


async def create_access_token(user_id : uuid.UUID):
    payload= {
        "sub" : str(user_id),
        "exp" : datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY_IN_MINUTES)
    }

    encoded_token = jwt.encode(
        payload=payload,
        algorithm=settings.ALGORITHM,
        key=settings.JWT_SECRET_KEY
    )

    return encoded_token


async def decode_token(token : str):
    payload = jwt.decode(
        token=token,
        algorithms=[settings.ALGORITHM],
        key=settings.JWT_SECRET_KEY
    )

    return payload



async def create_refresh_token():
    return secrets.token_urlsafe(64)
