"""Business logic service for URL shortening."""

from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.crud import (
    delete_slug_from_database,
    get_all_urls_paginated,
    get_click_stats_for_slug,
    get_long_url_by_slug,
    get_long_url_by_slug_from_database,
    get_url_by_long_url,
)
from src.database.crud import (
    record_click as record_click_db,
)
from src.exceptions import NoLongUrlFoundError
from src.shortener import calculate_expires_at
from src.shortener import generate_short_url as _generate_short_url


async def generate_short_url(
    long_url: str,
    session: AsyncSession,
    custom_slug: str | None = None,
    expires_in_days: int | None = None,
) -> tuple[str, bool, datetime | None]:
    """Generate short URL with optional custom slug and expiration.

    Args:
        long_url: Original long URL
        session: Database session
        custom_slug: Optional custom slug
        expires_in_days: Optional expiration in days

    Returns:
        Tuple of (slug, is_custom, expires_at)

    Raises:
        SlugAlreadyExistsError: If slug already exists
    """
    expires_at = calculate_expires_at(expires_in_days)
    slug, is_custom = await _generate_short_url(
        long_url,
        session,
        custom_slug=custom_slug,
        expires_at=expires_at,
    )
    return slug, is_custom, expires_at


async def get_url_by_slug(slug: str, session: AsyncSession) -> str:
    """Get long URL by slug.

    Args:
        slug: Short URL slug
        session: Database session

    Returns:
        Long URL string

    Raises:
        NoLongUrlFoundError: If URL not found or expired
    """
    long_url = await get_long_url_by_slug(slug, session)
    if not long_url:
        raise NoLongUrlFoundError("URL not found or expired")
    return long_url


async def get_url_info(slug: str, session: AsyncSession) -> dict[str, Any]:
    """Get detailed information about short URL.

    Args:
        slug: Short URL slug
        session: Database session

    Returns:
        Dictionary with URL information

    Raises:
        NoLongUrlFoundError: If URL not found
    """
    record = await get_long_url_by_slug_from_database(slug, session)
    if record is None:
        raise NoLongUrlFoundError("URL not found")

    click_stats = await get_click_stats_for_slug(slug, session)

    return {
        "slug": record.slug,
        "long_url": record.long_url,
        "custom_slug": record.custom_slug,
        "expires_at": record.expires_at,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
        "click_count": click_stats["total_clicks"],
    }


async def delete_url(slug: str, session: AsyncSession) -> bool:
    """Delete short URL.

    Args:
        slug: Short URL slug
        session: Database session

    Returns:
        True if deleted, False if not found
    """
    return await delete_slug_from_database(slug, session)


async def list_urls(
    session: AsyncSession,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[dict[str, Any]], int]:
    """Get paginated list of all short URLs.

    Args:
        session: Database session
        page: Page number (1-indexed)
        limit: Number of items per page

    Returns:
        Tuple of (list of URL info dictionaries, total count)
    """
    records, total = await get_all_urls_paginated(session, page, limit)

    items = []
    for record in records:
        click_stats = await get_click_stats_for_slug(record.slug, session)
        items.append(
            {
                "slug": record.slug,
                "long_url": record.long_url,
                "custom_slug": record.custom_slug,
                "expires_at": record.expires_at,
                "created_at": record.created_at,
                "updated_at": record.updated_at,
                "click_count": click_stats["total_clicks"],
            }
        )

    return items, total


async def check_existing_url(
    long_url: str,
    session: AsyncSession,
) -> str | None:
    """Check if long URL already has a short URL.

    Args:
        long_url: Original long URL
        session: Database session

    Returns:
        Existing slug if found, otherwise None
    """
    record = await get_url_by_long_url(long_url, session)
    if record and not record.is_expired():
        return record.slug
    return None


async def record_click(
    slug: str,
    session: AsyncSession,
    ip_address: str | None = None,
    user_agent: str | None = None,
    referer: str | None = None,
) -> None:
    """Record a click on a short URL.

    Args:
        slug: Short URL slug
        session: Database session
        ip_address: Client IP address
        user_agent: Client user agent
        referer: Referer header value
    """
    await record_click_db(slug, session, ip_address, user_agent, referer)
