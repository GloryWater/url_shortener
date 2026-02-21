"""ARQ worker for background tasks."""

import logging
from datetime import UTC, datetime
from typing import Any

from arq.connections import RedisSettings
from geoip2 import database as geoip2_database
from user_agents import parse as parse_user_agent

from src.config import Settings
from src.database.crud import create_click_enriched
from src.database.db import create_engine_and_session

logger = logging.getLogger(__name__)

# Queue names
QUEUE_CLICK_EVENT = "queue:click_event"
QUEUE_CLEANUP_EXPIRED = "queue:cleanup_expired"


def get_settings_cached() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings instance
    """
    from src.config import get_settings

    return get_settings()


async def process_click_event(
    ctx: dict[str, Any],  # noqa: ARG001
    slug: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
    referer: str | None = None,
) -> dict[str, Any]:
    """Process click event and enrich data.

    This background task:
    1. Parses user agent to extract browser, OS, device
    2. Converts IP to country/city using GeoIP
    3. Saves enriched click data to PostgreSQL

    Args:
        ctx: Task context
        slug: Short URL slug
        ip_address: Client IP address
        user_agent: Client user agent string
        referer: Referer header value

    Returns:
        Processing result
    """
    settings = get_settings_cached()
    _, async_session_maker = create_engine_and_session(settings)

    # Parse user agent
    browser = None
    os_name = None
    device = None
    if user_agent:
        try:
            ua = parse_user_agent(user_agent)
            browser = (
                f"{ua.browser.family} {ua.browser.version_string}"
                if ua.browser.family
                else None
            )
            os_name = f"{ua.os.family} {ua.os.version_string}" if ua.os.family else None
            device = ua.device.family if ua.device.family else None
        except Exception as e:
            logger.warning(f"Failed to parse user agent: {e}")

    # GeoIP lookup
    country = None
    city = None
    if ip_address and settings.geoip_db_path:
        try:
            reader = geoip2_database.Reader(settings.geoip_db_path)
            response = reader.city(ip_address)
            country = response.country.name
            city = response.city.name
            reader.close()
        except Exception as e:
            logger.debug(f"GeoIP lookup failed for {ip_address}: {e}")

    # Store enriched click data
    async with async_session_maker() as session:
        await create_click_enriched(
            slug=slug,
            session=session,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer,
            country=country,
            city=city,
            browser=browser,
            os=os_name,
            device=device,
        )
        logger.info(
            f"Processed click for slug={slug}, country={country}, browser={browser}"
        )

    return {
        "slug": slug,
        "country": country,
        "city": city,
        "browser": browser,
        "os": os_name,
        "device": device,
    }


async def cleanup_expired_urls(ctx: dict[str, Any]) -> dict[str, int]:  # noqa: ARG001
    """Clean up expired URLs.

    This scheduled task runs daily at 3 AM UTC and:
    1. Finds all expired URLs
    2. Deletes them from the database (clicks are deleted via CASCADE)
    3. Removes cached records

    Returns:
        Statistics about deleted URLs
    """
    settings = get_settings_cached()
    _, async_session_maker = create_engine_and_session(settings)

    from sqlalchemy import select

    from src.database.models import ShortURL

    deleted_count = 0

    async with async_session_maker() as session:
        # Find expired URLs
        query = select(ShortURL).filter(ShortURL.expires_at < datetime.now(UTC))
        result = await session.execute(query)
        expired_urls = result.scalars().all()

        # Delete expired URLs
        for url in expired_urls:
            await session.delete(url)
            deleted_count += 1

        await session.commit()

        # Clean up cache
        from src.cache import delete_cached_url

        for url in expired_urls:
            await delete_cached_url(url.slug, settings)

    logger.info(f"Cleaned up {deleted_count} expired URLs")
    return {"deleted_count": deleted_count}


# ARQ Worker Settings
class WorkerSettings:
    """ARQ worker configuration."""

    functions = [process_click_event, cleanup_expired_urls]
    cron_jobs = [
        # Run cleanup daily at 3 AM UTC
        {"coroutine": cleanup_expired_urls, "minute": 0, "hour": 3},
    ]
    max_jobs = 10
    job_timeout = 30
    burst = False

    def __init__(self) -> None:
        """Initialize worker settings."""
        settings = get_settings_cached()
        self.redis_settings = RedisSettings(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            database=settings.redis_db,
        )
