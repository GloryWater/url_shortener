"""Redis client and caching operations."""

import logging

import redis.asyncio as redis
from redis.asyncio.lock import Lock as RedisLock
from redis.exceptions import RedisError

from src.config import Settings

logger = logging.getLogger(__name__)

# Global Redis client instance
_redis_client: redis.Redis | None = None


async def get_redis_client(settings: Settings) -> redis.Redis:
    """Get or create Redis client.

    Args:
        settings: Application settings

    Returns:
        Redis client instance
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(  # type: ignore[no-untyped-call]
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def close_redis_client() -> None:
    """Close Redis client connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


async def get_cached_url(slug: str, settings: Settings) -> str | None:
    """Get URL from cache by slug.

    Args:
        slug: Short URL slug
        settings: Application settings

    Returns:
        Long URL or None if not found
    """
    try:
        client = await get_redis_client(settings)
        data = await client.get(f"url:{slug}")
        if data:
            logger.debug(f"Cache hit for slug: {slug}")
            return data.decode() if isinstance(data, bytes) else str(data)
        logger.debug(f"Cache miss for slug: {slug}")
        return None
    except RedisError as e:
        logger.error(f"Redis error getting cached URL: {e}")
        return None


async def cache_url(
    slug: str,
    long_url: str,
    settings: Settings,
    ttl: int | None = None,
) -> bool:
    """Cache URL by slug.

    Args:
        slug: Short URL slug
        long_url: Long URL to cache
        settings: Application settings
        ttl: Time to live in seconds

    Returns:
        True if successfully cached
    """
    try:
        client = await get_redis_client(settings)
        ttl = ttl or settings.redis_ttl
        await client.setex(f"url:{slug}", ttl, long_url)
        logger.debug(f"Cached URL for slug: {slug} (TTL: {ttl}s)")
        return True
    except RedisError as e:
        logger.error(f"Redis error caching URL: {e}")
        return False


async def delete_cached_url(slug: str, settings: Settings) -> bool:
    """Delete cached URL by slug.

    Args:
        slug: Short URL slug
        settings: Application settings

    Returns:
        True if successfully deleted
    """
    try:
        client = await get_redis_client(settings)
        await client.delete(f"url:{slug}")
        logger.debug(f"Deleted cached URL for slug: {slug}")
        return True
    except RedisError as e:
        logger.error(f"Redis error deleting cached URL: {e}")
        return False


async def acquire_distributed_lock(
    lock_name: str,
    settings: Settings,
    timeout: int = 10,
    blocking: bool = True,
    blocking_timeout: int = 5,
) -> RedisLock | None:
    """Acquire distributed lock in Redis.

    Args:
        lock_name: Lock name
        settings: Application settings
        timeout: Lock timeout in seconds
        blocking: Whether to block waiting for lock
        blocking_timeout: How long to wait for lock acquisition

    Returns:
        Lock instance or None if failed
    """
    try:
        client = await get_redis_client(settings)
        lock = client.lock(
            f"lock:{lock_name}",
            timeout=timeout,
            blocking=blocking,
            blocking_timeout=blocking_timeout,
        )
        acquired = await lock.acquire()
        if acquired:
            logger.debug(f"Acquired lock: {lock_name}")
            return lock
        logger.warning(f"Failed to acquire lock: {lock_name}")
        return None
    except RedisError as e:
        logger.error(f"Redis error acquiring lock: {e}")
        return None


async def release_distributed_lock(lock: RedisLock) -> bool:
    """Release distributed lock.

    Args:
        lock: Lock instance to release

    Returns:
        True if successfully released
    """
    try:
        await lock.release()
        logger.debug(f"Released lock: {str(lock.name)}")  # noqa: STR001
        return True
    except RedisError as e:
        logger.error(f"Redis error releasing lock: {e}")
        return False


# Cache metrics
async def increment_cache_hits(settings: Settings) -> None:
    """Increment cache hits counter."""
    try:
        client = await get_redis_client(settings)
        await client.incr("metrics:cache:hits")
    except RedisError:
        pass


async def increment_cache_misses(settings: Settings) -> None:
    """Increment cache misses counter."""
    try:
        client = await get_redis_client(settings)
        await client.incr("metrics:cache:misses")
    except RedisError:
        pass


async def get_cache_stats(settings: Settings) -> dict[str, int]:
    """Get cache statistics.

    Args:
        settings: Application settings

    Returns:
        Dictionary with cache statistics
    """
    try:
        client = await get_redis_client(settings)
        hits = await client.get("metrics:cache:hits")
        misses = await client.get("metrics:cache:misses")
        return {
            "hits": int(hits) if hits else 0,
            "misses": int(misses) if misses else 0,
        }
    except RedisError:
        return {"hits": 0, "misses": 0}
