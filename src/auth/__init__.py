"""Authentication module."""

from src.auth.crud import create_user, get_user_by_email, get_user_by_id
from src.auth.dependencies import get_current_user
from src.auth.jwt import create_access_token, decode_access_token, get_password_hash
from src.auth.router import router
from src.auth.schemas import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

__all__ = [
    "router",
    "get_current_user",
    "create_access_token",
    "decode_access_token",
    "get_password_hash",
    "create_user",
    "get_user_by_email",
    "get_user_by_id",
    "TokenResponse",
    "UserLoginRequest",
    "UserRegisterRequest",
    "UserResponse",
]
