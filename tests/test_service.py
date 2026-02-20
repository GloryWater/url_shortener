"""Service layer tests for URL shortener."""

from datetime import UTC

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Click, ShortURL
from src.exceptions import NoLongUrlFoundError
from src.service import (
    check_existing_url,
    delete_url,
    generate_short_url,
    get_url_by_slug,
    get_url_info,
    list_urls,
    record_click,
)
from src.shortener import (
    calculate_expires_at,
    generate_random_slug,
    is_valid_custom_slug,
)

# ============================================
# Slug Generation Tests
# ============================================


async def test_generate_short_url(session: AsyncSession) -> None:
    """Test short URL generation."""
    slug, is_custom, expires_at = await generate_short_url(
        "https://google.com", session
    )
    assert isinstance(slug, str)
    assert len(slug) == 6
    assert is_custom is False
    assert expires_at is None


async def test_generate_short_url_stored_in_db(session: AsyncSession) -> None:
    """Test that generated URL is stored in database."""
    slug, _, _ = await generate_short_url("https://test.com", session)

    query = select(ShortURL).filter_by(slug=slug)
    result = await session.execute(query)
    stored = result.scalar_one_or_none()

    assert stored is not None
    assert stored.long_url == "https://test.com"
    assert stored.custom_slug is False


async def test_generate_short_url_with_custom_slug(session: AsyncSession) -> None:
    """Test short URL generation with custom slug."""
    slug, is_custom, expires_at = await generate_short_url(
        "https://example.com",
        session,
        custom_slug="mylink",
    )
    assert slug == "mylink"
    assert is_custom is True


async def test_generate_short_url_with_expiration(session: AsyncSession) -> None:
    """Test short URL generation with expiration."""
    slug, is_custom, expires_at = await generate_short_url(
        "https://example.com",
        session,
        expires_in_days=30,
    )
    assert expires_at is not None
    assert is_custom is False


async def test_generate_short_url_unique(session: AsyncSession) -> None:
    """Test uniqueness of generated slugs."""
    slugs: set[str] = set()
    for _ in range(20):
        slug, _, _ = await generate_short_url("https://unique.com", session)
        slugs.add(slug)

    # All slugs should be unique
    assert len(slugs) == 20


# ============================================
# Get URL Tests
# ============================================


async def test_get_url_by_slug(session: AsyncSession) -> None:
    """Test getting URL by slug."""
    long_url = "https://example.org"
    slug, _, _ = await generate_short_url(long_url, session)

    result = await get_url_by_slug(slug, session)
    assert result == long_url


async def test_get_url_by_slug_not_found(session: AsyncSession) -> None:
    """Test getting non-existent URL."""
    with pytest.raises(NoLongUrlFoundError):
        await get_url_by_slug("nonexistent", session)


async def test_get_url_info(session: AsyncSession) -> None:
    """Test getting detailed URL information."""
    long_url = "https://info-test.com"
    slug, _, _ = await generate_short_url(long_url, session)

    info = await get_url_info(slug, session)
    assert info["slug"] == slug
    assert info["long_url"] == long_url
    assert "click_count" in info
    assert "created_at" in info


# ============================================
# Delete URL Tests
# ============================================


async def test_delete_url(session: AsyncSession) -> None:
    """Test deleting a URL."""
    slug, _, _ = await generate_short_url("https://delete-test.com", session)

    # Delete
    result = await delete_url(slug, session)
    assert result is True

    # Verify deletion
    with pytest.raises(NoLongUrlFoundError):
        await get_url_by_slug(slug, session)


async def test_delete_url_not_found(session: AsyncSession) -> None:
    """Test deleting non-existent URL."""
    result = await delete_url("nonexistent", session)
    assert result is False


# ============================================
# List URLs Tests
# ============================================


async def test_list_urls(session: AsyncSession) -> None:
    """Test listing URLs."""
    # Create some URLs
    for i in range(15):
        await generate_short_url(f"https://example{i}.com", session)

    items, total = await list_urls(session, page=1, limit=10)
    assert len(items) == 10
    assert total == 15


async def test_list_urls_pagination(session: AsyncSession) -> None:
    """Test URL list pagination."""
    # Create 25 URLs
    for i in range(25):
        await generate_short_url(f"https://page{i}.com", session)

    # First page
    items1, total1 = await list_urls(session, page=1, limit=10)
    assert len(items1) == 10
    assert total1 == 25

    # Second page
    items2, total2 = await list_urls(session, page=2, limit=10)
    assert len(items2) == 10


# ============================================
# Duplicate URL Detection Tests
# ============================================


async def test_check_existing_url(session: AsyncSession) -> None:
    """Test checking for existing URL."""
    long_url = "https://existing.com"
    slug1, _, _ = await generate_short_url(long_url, session)

    result = await check_existing_url(long_url, session)
    assert result == slug1


async def test_check_existing_url_not_found(session: AsyncSession) -> None:
    """Test checking non-existent URL."""
    result = await check_existing_url("https://not-existing.com", session)
    assert result is None


# ============================================
# Click Analytics Tests
# ============================================


async def test_record_click(session: AsyncSession) -> None:
    """Test recording a click."""
    slug, _, _ = await generate_short_url("https://click-test.com", session)

    await record_click(
        slug,
        session,
        ip_address="192.168.1.1",
        user_agent="Test Browser",
        referer="https://google.com",
    )

    # Verify click was recorded
    query = select(Click).filter_by(slug=slug)
    result = await session.execute(query)
    click = result.scalar_one_or_none()

    assert click is not None
    assert click.ip_address == "192.168.1.1"
    assert click.user_agent == "Test Browser"
    assert click.referer == "https://google.com"


async def test_get_url_info_with_clicks(session: AsyncSession) -> None:
    """Test URL info includes click count."""
    slug, _, _ = await generate_short_url("https://stats-test.com", session)

    # Record some clicks
    for _ in range(5):
        await record_click(slug, session)

    info = await get_url_info(slug, session)
    assert info["click_count"] == 5


# ============================================
# Random Slug Tests
# ============================================


def test_generate_random_slug() -> None:
    """Test random slug generation."""
    slug = generate_random_slug()
    assert len(slug) == 6
    assert slug.isalnum()


def test_generate_random_slug_custom_length() -> None:
    """Test random slug with custom length."""
    slug = generate_random_slug(length=10)
    assert len(slug) == 10


def test_is_valid_custom_slug_valid() -> None:
    """Test valid custom slug validation."""
    assert is_valid_custom_slug("test123") is True
    assert is_valid_custom_slug("abcd") is True
    assert is_valid_custom_slug("ABCD1234") is True


def test_is_valid_custom_slug_invalid() -> None:
    """Test invalid custom slug validation."""
    assert is_valid_custom_slug("ab") is False  # Too short
    assert is_valid_custom_slug("toolongslug123") is False  # Too long
    assert is_valid_custom_slug("test-link") is False  # Invalid char
    assert is_valid_custom_slug("test_link") is False  # Invalid char


# ============================================
# Expiration Tests
# ============================================


def test_calculate_expires_at_none() -> None:
    """Test expiration calculation with None."""
    result = calculate_expires_at(None)
    assert result is None


def test_calculate_expires_at_days() -> None:
    """Test expiration calculation with days."""
    from datetime import datetime, timedelta

    result = calculate_expires_at(30)
    expected = datetime.now(UTC) + timedelta(days=30)

    # Compare with small tolerance for timing
    diff = abs((result - expected).total_seconds())
    assert diff < 1  # Less than 1 second difference


# ============================================
# Edge Cases
# ============================================


async def test_generate_short_url_special_chars(session: AsyncSession) -> None:
    """Test URL with special characters."""
    long_url = "https://example.com/path?param=value&other=123"
    slug, _, _ = await generate_short_url(long_url, session)
    assert len(slug) == 6


async def test_get_url_info_expired(session: AsyncSession) -> None:
    """Test getting expired URL raises error."""
    from datetime import datetime, timedelta

    # Create URL that expires in the past by directly manipulating the model
    from src.database.models import ShortURL

    expired_url = ShortURL(
        slug="expired123",
        long_url="https://expired.com",
        expires_at=datetime.now(UTC) - timedelta(days=1),
    )
    session.add(expired_url)
    await session.commit()

    # Should raise error for expired URL
    with pytest.raises(NoLongUrlFoundError):
        await get_url_by_slug("expired123", session)
