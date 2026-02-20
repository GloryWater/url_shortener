"""Rate limiting configuration using slowapi."""

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config import Settings


def create_limiter(settings: Settings) -> Limiter:
    """Create rate limiter instance.

    Args:
        settings: Application settings

    Returns:
        Configured Limiter instance
    """
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[
            f"{settings.app.rate_limit_per_hour}/hour",
            f"{settings.app.rate_limit_per_minute}/minute",
        ],
        storage_uri="memory://",
    )
    return limiter
