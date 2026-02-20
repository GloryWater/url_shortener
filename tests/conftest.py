from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.database.models import Base
from src.main import app, get_session

# Используем in-memory SQLite для тестов
engine = create_async_engine(
    url="sqlite+aiosqlite:///:memory:",
    echo=False,
)

new_session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
    async with new_session() as session:
        yield session


app.dependency_overrides[get_session] = get_test_session


@pytest.fixture(scope="function", autouse=True)
async def setup_db() -> AsyncGenerator[None, None]:
    """Создаем таблицы перед каждым тестом."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для доступа к сессии БД в тестах."""
    async with new_session() as session:
        yield session


@pytest.fixture(scope="function")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    """Фикстура для асинхронного HTTP клиента."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
