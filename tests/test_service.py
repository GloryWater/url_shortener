import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.models import ShortURL
from src.exceptions import NoLongUrlFoundError
from src.service import generate_short_url, get_url_by_slug
from src.shortener import generate_random_slug


async def test_generate_short_url(session: AsyncSession) -> None:
    """Тест генерации короткой ссылки."""
    res = await generate_short_url("https://google.com", session)
    assert isinstance(res, str)
    assert len(res) == 6


async def test_generate_short_url_stored_in_db(session: AsyncSession) -> None:
    """Тест сохранения ссылки в БД."""
    slug = await generate_short_url("https://test.com", session)

    # Проверяем, что ссылка сохранена в БД
    query = select(ShortURL).filter_by(slug=slug)
    result = await session.execute(query)
    stored = result.scalar_one_or_none()

    assert stored is not None
    assert stored.long_url == "https://test.com"


async def test_get_url_by_slug(session: AsyncSession) -> None:
    """Тест получения ссылки по slug."""
    long_url = "https://example.org"
    slug = await generate_short_url(long_url, session)

    result = await get_url_by_slug(slug, session)
    assert result == long_url


async def test_get_url_by_slug_not_found(session: AsyncSession) -> None:
    """Тест получения несуществующей ссылки."""
    with pytest.raises(NoLongUrlFoundError):
        await get_url_by_slug("nonexistent", session)


def test_generate_random_slug() -> None:
    """Тест генерации случайного slug."""
    slug = generate_random_slug()
    assert len(slug) == 6
    assert slug.isalnum()


def test_generate_random_slug_custom_length() -> None:
    """Тест генерации slug с кастомной длиной."""
    slug = generate_random_slug(length=10)
    assert len(slug) == 10


async def test_generate_short_url_unique(session: AsyncSession) -> None:
    """Тест уникальности сгенерированных slug."""
    slugs: set[str] = set()
    for _ in range(20):
        slug = await generate_short_url("https://unique.com", session)
        slugs.add(slug)

    # Все slug должны быть уникальными
    assert len(slugs) == 20
