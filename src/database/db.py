"""Database connection and session management."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import Settings


def create_engine_and_session(
    settings: Settings,
) -> tuple[Any, async_sessionmaker[AsyncSession]]:
    """Create SQLAlchemy engine and session factory.

    Args:
        settings: Application settings

    Returns:
        Tuple of (engine, async_sessionmaker)
    """
    engine = create_async_engine(
        url=settings.database_url,
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,  # Enable connection health checks
        echo=settings.sql_echo,
    )

    async_session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return engine, async_session_maker
