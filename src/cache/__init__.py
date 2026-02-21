"""Caching module."""

from src.cache.redis_client import (
    acquire_distributed_lock,
    cache_url,
    close_redis_client,
    delete_cached_url,
    get_cache_stats,
    get_cached_url,
    get_redis_client,
    increment_cache_hits,
    increment_cache_misses,
    release_distributed_lock,
)

__all__ = [
    "get_redis_client",
    "close_redis_client",
    "get_cached_url",
    "cache_url",
    "delete_cached_url",
    "acquire_distributed_lock",
    "release_distributed_lock",
    "increment_cache_hits",
    "increment_cache_misses",
    "get_cache_stats",
]
