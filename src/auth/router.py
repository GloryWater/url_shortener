"""Authentication router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.crud import create_user, get_user_by_email
from src.auth.dependencies import get_current_user
from src.auth.jwt import create_access_token, get_password_hash
from src.auth.schemas import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from src.config import Settings, get_settings
from src.database.db import create_engine_and_session
from src.database.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_session(settings: Settings) -> AsyncSession:
    """Create database session.

    Args:
        settings: Application settings

    Returns:
        AsyncSession instance
    """
    _, async_session_maker = create_engine_and_session(settings)
    return async_session_maker()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email and password",
)
async def register(
    body: UserRegisterRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserResponse:
    """Register a new user.

    Args:
        body: Registration request body
        settings: Application settings

    Returns:
        Created user information

    Raises:
        HTTPException: If email already exists
    """
    session = get_session(settings)
    async with session:
        # Check if user exists
        existing_user = await get_user_by_email(body.email, session)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create user
        hashed_password = get_password_hash(body.password)
        user = await create_user(body.email, hashed_password, session)
        return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description="Authenticate user and return JWT access token",
)
async def login(
    body: UserLoginRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    """Login user and return JWT token.

    Args:
        body: Login request body
        settings: Application settings

    Returns:
        JWT access token

    Raises:
        HTTPException: If credentials are invalid
    """
    session = get_session(settings)
    async with session:
        # Get user
        user = await get_user_by_email(body.email, session)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not get_password_hash(body.password) == user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            settings=settings,
        )

        return TokenResponse(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get information about currently authenticated user",
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    return UserResponse.model_validate(current_user)
