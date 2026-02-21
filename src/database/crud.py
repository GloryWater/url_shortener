"""Database CRUD operations for URL shortening."""

from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Click, ShortURL
from src.exceptions import SlugAlreadyExistsError


async def add_slug_to_database(
    slug: str,
    long_url: str,
    session: AsyncSession,
    custom_slug: bool = False,
    expires_at: datetime | None = None,
) -> ShortURL:
    """Add a new short URL to the database.

    Args:
        slug: Short URL slug
        long_url: Original long URL
        session: Database session
        custom_slug: Whether the slug was user-provided
        expires_at: Optional expiration date

    Returns:
        Created ShortURL instance

    Raises:
        SlugAlreadyExistsError: If slug already exists
    """
    new_slug = ShortURL(
        slug=slug,
        long_url=long_url,
        custom_slug=custom_slug,
        expires_at=expires_at,
    )
    session.add(new_slug)
    try:
        await session.commit()
        await session.refresh(new_slug)
        return new_slug
    except IntegrityError:
        await session.rollback()
        raise SlugAlreadyExistsError


async def get_long_url_by_slug_from_database(
    slug: str,
    session: AsyncSession,
) -> ShortURL | None:
    """Get short URL record by slug.

    Args:
        slug: Short URL slug
        session: Database session

    Returns:
        ShortURL instance or None if not found
    """
    query = select(ShortURL).filter(ShortURL.slug == slug)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_long_url_by_slug(
    slug: str,
    session: AsyncSession,
) -> str | None:
    """Get long URL by slug (helper method).

    Args:
        slug: Short URL slug
        session: Database session

    Returns:
        Long URL string or None if not found
    """
    record = await get_long_url_by_slug_from_database(slug, session)
    if record is None or record.is_expired():
        return None
    return record.long_url


async def delete_slug_from_database(
    slug: str,
    session: AsyncSession,
) -> bool:
    """Delete short URL by slug.

    Args:
        slug: Short URL slug to delete
        session: Database session

    Returns:
        True if deleted, False if not found
    """
    query = select(ShortURL).filter(ShortURL.slug == slug)
    result = await session.execute(query)
    record = result.scalar_one_or_none()

    if record is None:
        return False

    await session.delete(record)
    await session.commit()
    return True


async def get_all_urls_paginated(
    session: AsyncSession,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[ShortURL], int]:
    """Get paginated list of all short URLs.

    Args:
        session: Database session
        page: Page number (1-indexed)
        limit: Number of items per page

    Returns:
        Tuple of (list of ShortURL records, total count)
    """
    # Get total count
    count_query = select(func.count(ShortURL.slug))
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated records
    query = (
        select(ShortURL)
        .order_by(ShortURL.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    result = await session.execute(query)
    records = result.scalars().all()

    return list(records), total


async def get_url_by_long_url(
    long_url: str,
    session: AsyncSession,
) -> ShortURL | None:
    """Check if long URL already has a short URL.

    Args:
        long_url: Original long URL
        session: Database session

    Returns:
        ShortURL instance if exists, otherwise None
    """
    query = select(ShortURL).filter(ShortURL.long_url == long_url)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def record_click(
    slug: str,
    session: AsyncSession,
    ip_address: str | None = None,
    user_agent: str | None = None,
    referer: str | None = None,
) -> Click:
    """Record a click on a short URL for analytics.

    Args:
        slug: Short URL slug that was clicked
        session: Database session
        ip_address: Client IP address
        user_agent: Client user agent string
        referer: Referer header value

    Returns:
        Created Click instance
    """
    click = Click(
        slug=slug,
        ip_address=ip_address,
        user_agent=user_agent,
        referer=referer,
    )
    session.add(click)
    await session.commit()
    await session.refresh(click)
    return click


async def create_click_enriched(
    slug: str,
    session: AsyncSession,
    ip_address: str | None = None,
    user_agent: str | None = None,
    referer: str | None = None,
    country: str | None = None,
    city: str | None = None,
    browser: str | None = None,
    os: str | None = None,
    device: str | None = None,
) -> Click:
    """Create an enriched click record.

    Args:
        slug: Short URL slug that was clicked
        session: Database session
        ip_address: Client IP address
        user_agent: Client user agent string
        referer: Referer header value
        country: Country from GeoIP
        city: City from GeoIP
        browser: Browser from user agent parsing
        os: Operating system from user agent parsing
        device: Device type from user agent parsing

    Returns:
        Created Click instance
    """
    click = Click(
        slug=slug,
        ip_address=ip_address,
        user_agent=user_agent,
        referer=referer,
        country=country,
        city=city,
        browser=browser,
        os=os,
        device=device,
    )
    session.add(click)
    await session.commit()
    await session.refresh(click)
    return click


async def get_click_count_for_slug(
    slug: str,
    session: AsyncSession,
) -> int:
    """Get total click count for a short URL.

    Args:
        slug: Short URL slug
        session: Database session

    Returns:
        Total number of clicks
    """
    query = select(func.count(Click.id)).filter(Click.slug == slug)
    result = await session.execute(query)
    return result.scalar() or 0


async def get_click_stats_for_slug(
    slug: str,
    session: AsyncSession,
) -> dict[str, Any]:
    """Get detailed click statistics for a short URL.

    Args:
        slug: Short URL slug
        session: Database session

    Returns:
        Dictionary with click statistics
    """
    # Total clicks
    total_query = select(func.count(Click.id)).filter(Click.slug == slug)
    total_result = await session.execute(total_query)
    total_clicks = total_result.scalar() or 0

    # Last click
    last_click_query = (
        select(Click.clicked_at)
        .filter(Click.slug == slug)
        .order_by(Click.clicked_at.desc())
        .limit(1)
    )
    last_click_result = await session.execute(last_click_query)
    last_click = last_click_result.scalar_one_or_none()

    # Unique IPs
    unique_ips_query = select(func.count(func.distinct(Click.ip_address))).filter(
        Click.slug == slug,
        Click.ip_address.isnot(None),
    )
    unique_ips_result = await session.execute(unique_ips_query)
    unique_ips = unique_ips_result.scalar() or 0

    return {
        "total_clicks": total_clicks,
        "last_click": last_click.isoformat() if last_click else None,
        "unique_ips": unique_ips,
    }
