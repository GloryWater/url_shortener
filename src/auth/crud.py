"""CRUD operations for users."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User


async def get_user_by_email(
    email: str,
    session: AsyncSession,
) -> User | None:
    """Get user by email.

    Args:
        email: User email
        session: Database session

    Returns:
        User instance or None if not found
    """
    query = select(User).filter(User.email == email)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_id(
    user_id: int,
    session: AsyncSession,
) -> User | None:
    """Get user by ID.

    Args:
        user_id: User ID
        session: Database session

    Returns:
        User instance or None if not found
    """
    query = select(User).filter(User.id == user_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def create_user(
    email: str,
    hashed_password: str,
    session: AsyncSession,
    is_superuser: bool = False,
) -> User:
    """Create a new user.

    Args:
        email: User email
        hashed_password: Hashed password
        session: Database session
        is_superuser: Whether the user is a superuser

    Returns:
        Created User instance
    """
    user = User(
        email=email,
        hashed_password=hashed_password,
        is_superuser=is_superuser,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(
    user: User,
    session: AsyncSession,
    **kwargs: dict[str, Any],
) -> User:
    """Update a user.

    Args:
        user: User instance to update
        session: Database session
        kwargs: Fields to update

    Returns:
        Updated User instance
    """
    for field, value in kwargs.items():
        if hasattr(user, field):
            setattr(user, field, value)
    await session.commit()
    await session.refresh(user)
    return user


async def delete_user(
    user: User,
    session: AsyncSession,
) -> bool:
    """Delete a user.

    Args:
        user: User instance to delete
        session: Database session

    Returns:
        True if deleted, False if not found
    """
    await session.delete(user)
    await session.commit()
    return True
