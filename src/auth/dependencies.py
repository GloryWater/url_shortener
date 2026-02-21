"""Authentication dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.crud import get_user_by_id
from src.auth.jwt import decode_access_token
from src.config import Settings, get_settings
from src.database.db import create_engine_and_session
from src.database.models import User

security = HTTPBearer(auto_error=False)


def get_auth_session() -> AsyncSession:
    """Get database session for authentication dependencies.

    Returns:
        AsyncSession instance
    """
    settings = get_settings()
    _, async_session_maker = create_engine_and_session(settings)
    return async_session_maker()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    """Get current authenticated user.

    Args:
        credentials: HTTP authorization credentials
        settings: Application settings

    Returns:
        User instance

    Raises:
        HTTPException: If authentication fails
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_access_token(token, settings)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: int | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create session for this request
    _, async_session_maker = create_engine_and_session(settings)
    async with async_session_maker() as session:
        user = await get_user_by_id(int(user_id), session)

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user
