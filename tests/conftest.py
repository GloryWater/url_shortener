"""Pytest fixtures for URL shortener tests."""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.config import Settings
from src.database.models import Base
from src.main import app, get_session


# Test settings
@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Create test settings."""
    return Settings()


# In-memory SQLite for tests
engine = create_async_engine(
    url="sqlite+aiosqlite:///:memory:",
    echo=False,
)

new_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
    """Override get_session dependency for tests."""
    async with new_session() as session:
        yield session


async def get_test_auth_session() -> AsyncGenerator[AsyncSession, None]:
    """Override get_auth_session dependency for auth tests."""
    async with new_session() as session:
        yield session


# Override dependencies for tests
app.dependency_overrides[get_session] = get_test_session


# Override auth session dependency - import here to avoid circular imports
def _override_auth_dependency() -> None:
    """Override auth session dependency for tests."""
    from src.auth.router import get_auth_session

    app.dependency_overrides[get_auth_session] = get_test_auth_session


_override_auth_dependency()

# Disable rate limiting for tests
app.state.limiter.enabled = False


@pytest.fixture(scope="function", autouse=True)
async def setup_db() -> AsyncGenerator[None, None]:
    """Create database tables before each test."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    """Provide database session for tests."""
    async with new_session() as session:
        yield session


@pytest.fixture(scope="function")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    """Provide async HTTP client for tests."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
def sample_long_url() -> str:
    """Sample long URL for tests."""
    return "https://example.com/test/path?param=value"


@pytest.fixture
def sample_custom_slug() -> str:
    """Sample custom slug for tests."""
    return "mytest"


@pytest.fixture
def sample_expires_in_days() -> int:
    """Sample expiration days for tests."""
    return 30
