"""Custom exceptions for the URL shortener application."""


class ShortenerBaseError(Exception):
    """Base exception for all URL shortener errors."""

    pass


class NoLongUrlFoundError(ShortenerBaseError):
    """Raised when short URL is not found or expired."""

    pass


class SlugAlreadyExistsError(ShortenerBaseError):
    """Raised when attempting to create a slug that already exists."""

    pass


class InvalidCustomSlugError(ShortenerBaseError):
    """Raised when custom slug format is invalid."""

    pass


class URLExpiredError(ShortenerBaseError):
    """Raised when accessing an expired short URL."""

    pass


class RateLimitExceededError(ShortenerBaseError):
    """Raised when rate limit is exceeded."""

    pass
