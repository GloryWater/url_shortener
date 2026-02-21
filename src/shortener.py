"""Slug generation utilities."""

import re
import string
from datetime import UTC, datetime, timedelta
from secrets import choice
from typing import TYPE_CHECKING, Any

from src.exceptions import SlugAlreadyExistsError

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from sqlalchemy.ext.asyncio import AsyncSession

ALPHABET: str = string.ascii_letters + string.digits
SLUG_LENGTH = 6
MAX_ATTEMPTS = 5

# Pattern for valid custom slugs
CUSTOM_SLUG_PATTERN = re.compile(r"^[a-zA-Z0-9]{4,12}$")


def generate_random_slug(length: int = SLUG_LENGTH) -> str:
    """Generate random alphanumeric slug.

    Args:
        length: Length of generated slug

    Returns:
        Random slug string
    """
    return "".join(choice(ALPHABET) for _ in range(length))


def is_valid_custom_slug(slug: str) -> bool:
    """Validate custom slug format.

    Args:
        slug: Custom slug to validate

    Returns:
        True if valid, otherwise False
    """
    return bool(CUSTOM_SLUG_PATTERN.match(slug))


def calculate_expires_at(days: int | None) -> datetime | None:
    """Calculate expiration datetime.

    Args:
        days: Number of days until expiration

    Returns:
        Expiration datetime or None if no expiration
    """
    if days is None:
        return None
    return datetime.now(UTC) + timedelta(days=days)


async def generate_short_url(
    long_url: str,
    session: "AsyncSession",
    custom_slug: str | None = None,
    expires_at: datetime | None = None,
    add_to_db_func: "Callable[[str, str, AsyncSession, bool, datetime | None], Coroutine[Any, Any, Any]] | None" = None,
) -> tuple[str, bool]:
    """Generate short URL slug.

    Args:
        long_url: Original long URL
        session: Database session
        custom_slug: Optional custom slug provided by user
        expires_at: Optional expiration datetime
        add_to_db_func: Optional custom database add function

    Returns:
        Tuple of (slug, is_custom)

    Raises:
        SlugAlreadyExistsError: If custom slug already exists or
            failed to generate unique slug after maximum attempts
    """
    from src.database.crud import add_slug_to_database

    if add_to_db_func is None:
        add_to_db_func = add_slug_to_database

    # Handle custom slug
    if custom_slug:
        if not is_valid_custom_slug(custom_slug):
            raise ValueError("Custom slug must be 4-12 alphanumeric characters")
        try:
            await add_to_db_func(
                custom_slug,
                long_url,
                session,
                custom_slug=True,
                expires_at=expires_at,  # type: ignore[call-arg]
            )
            return custom_slug, True
        except SlugAlreadyExistsError as ex:
            raise SlugAlreadyExistsError(
                f"Custom slug '{custom_slug}' already exists"
            ) from ex

    # Generate random slug
    for attempt in range(MAX_ATTEMPTS):
        slug = generate_random_slug()
        try:
            await add_to_db_func(
                slug,
                long_url,
                session,
                custom_slug=False,
                expires_at=expires_at,  # type: ignore[call-arg]
            )
            return slug, False
        except SlugAlreadyExistsError as ex:
            if attempt == MAX_ATTEMPTS - 1:
                raise SlugAlreadyExistsError(
                    f"Failed to generate unique slug after {MAX_ATTEMPTS} attempts"
                ) from ex

    # This should never be reached, but included for type checker
    raise SlugAlreadyExistsError
