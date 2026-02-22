"""FastAPI application entry point."""

import logging
import os
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi.errors import RateLimitExceeded
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.router import router as auth_router
from src.cache import cache_url, close_redis_client, get_cached_url
from src.config import get_settings
from src.database.db import create_engine_and_session
from src.database.models import Base
from src.exceptions import (
    NoLongUrlFoundError,
    ShortenerBaseError,
    SlugAlreadyExistsError,
)
from src.logging_config import setup_logging
from src.rate_limiter import create_limiter
from src.schemas import (
    ClickStatsResponse,
    DeleteResponse,
    HealthResponse,
    ShortenUrlRequest,
    ShortenUrlResponse,
    UrlInfoResponse,
    UrlListResponse,
)
from src.service import (
    check_existing_url,
    delete_url,
    generate_short_url,
    get_url_by_slug,
    get_url_info,
    list_urls,
)

logger = logging.getLogger(__name__)

# Initialize settings
settings = get_settings()

# Setup logging
setup_logging(
    settings, is_production=os.getenv("ENVIRONMENT", "development") == "production"
)

# Create engine and session
engine, async_session_maker = create_engine_and_session(settings)

# Create rate limiter
limiter = create_limiter(settings)

# Worker instance
_worker = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    # Startup: create database tables
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    # Setup Prometheus metrics
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    yield

    # Shutdown: cleanup
    await engine.dispose()
    await close_redis_client()

    if _worker:
        _worker.close()


# Initialize FastAPI application
app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
    description="High-performance URL shortener with analytics, caching, and authentication",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")

# Add rate limiter to application
app.state.limiter = limiter


# ============================================
# Exception Handlers
# ============================================


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(
    request: Request,
    exc: RateLimitExceeded,
) -> JSONResponse:
    """Handle rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {str(exc)}"},
    )


@app.exception_handler(ShortenerBaseError)
async def shortener_error_handler(
    request: Request,
    exc: ShortenerBaseError,
) -> JSONResponse:
    """Handle custom shortener errors."""
    status_code = (
        status.HTTP_404_NOT_FOUND
        if isinstance(exc, NoLongUrlFoundError)
        else status.HTTP_409_CONFLICT
    )
    return JSONResponse(
        status_code=status_code,
        content={"detail": str(exc)},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unhandled exceptions."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# ============================================
# Middleware
# ============================================


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Add security headers to all responses."""
    response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data: https:;"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    return response


# ============================================
# Dependencies
# ============================================


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session_maker() as session:
        yield session


def get_client_ip(request: Request) -> str | None:
    """Get client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return str(forwarded.split(",")[0].strip())
    return str(request.client.host) if request.client else None


def get_user_agent(request: Request) -> str | None:
    """Get user agent from request."""
    return str(request.headers.get("User-Agent")) or None


def get_referer(request: Request) -> str | None:
    """Get referer from request."""
    return str(request.headers.get("Referer")) or None


# ============================================
# Metrics Endpoint (must be before legacy routes)
# ============================================


@app.get("/metrics", include_in_schema=False)
async def get_metrics() -> str:
    """Return Prometheus metrics.

    Note: This is a fallback endpoint. The Instrumentator
    registers its own /metrics endpoint during lifespan.
    """
    return "# Prometheus metrics available via Instrumentator\n"


# ============================================
# API v1 Routes
# ============================================


@app.get("/", tags=["Root"])
async def read_root() -> FileResponse:
    """Serve the main frontend HTML page (index.html)."""
    return FileResponse("index.html")


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> HealthResponse:
    """Health check endpoint."""
    db_status = "connected"
    try:
        from sqlalchemy import text

        await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "unhealthy",
        version=settings.app_version,
        database=db_status,
    )


# API v1 prefix
API_V1_PREFIX = "/api/v1"


@app.post(
    "/api/v1/urls",
    response_model=ShortenUrlResponse,
    tags=["URLs"],
    summary="Create short URL",
    description="Create a shortened URL with optional custom slug and expiration",
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def create_short_url(
    request: Request,
    body: ShortenUrlRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ShortenUrlResponse:
    """Create a new short URL."""
    long_url_str = str(body.long_url)

    # Check for existing URL (avoid duplicates)
    existing_slug = await check_existing_url(long_url_str, session)
    if existing_slug:
        return ShortenUrlResponse(
            data=existing_slug,
            short_url=f"{request.base_url}{existing_slug}",
            long_url=long_url_str,
            custom_slug=False,
            expires_at=None,
        )

    # Calculate expiration
    from src.shortener import calculate_expires_at

    expires_at = calculate_expires_at(body.expires_in_days)

    # Generate short URL
    try:
        slug, is_custom, expires_at = await generate_short_url(
            long_url_str,
            session,
            custom_slug=body.custom_slug,
            expires_in_days=body.expires_in_days,
        )
    except SlugAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    return ShortenUrlResponse(
        data=slug,
        short_url=f"{request.base_url}{slug}",
        long_url=long_url_str,
        custom_slug=is_custom,
        expires_at=expires_at,
    )


@app.get(
    "/api/v1/urls",
    response_model=UrlListResponse,
    tags=["URLs"],
    summary="List all URLs",
    description="Get paginated list of all shortened URLs",
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def list_all_urls(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    page: int = 1,
    limit: int = 20,
) -> UrlListResponse:
    """List all shortened URLs with pagination."""
    items, total = await list_urls(session, page, limit)
    pages = (total + limit - 1) // limit

    return UrlListResponse(
        items=[UrlInfoResponse(**item) for item in items],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@app.get(
    "/api/v1/urls/{slug}",
    response_model=UrlInfoResponse,
    tags=["URLs"],
    summary="Get URL info",
    description="Get detailed information about a shortened URL",
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_url_details(
    request: Request,
    slug: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UrlInfoResponse:
    """Get detailed information about a short URL."""
    url_info = await get_url_info(slug, session)
    return UrlInfoResponse(**url_info)


@app.delete(
    "/api/v1/urls/{slug}",
    response_model=DeleteResponse,
    tags=["URLs"],
    summary="Delete URL",
    description="Delete a shortened URL",
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def delete_short_url(
    request: Request,
    slug: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DeleteResponse:
    """Delete a short URL."""
    success = await delete_url(slug, session)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found",
        )
    return DeleteResponse(
        success=True,
        message="URL successfully deleted",
    )


@app.get(
    "/api/v1/urls/{slug}/stats",
    response_model=ClickStatsResponse,
    tags=["Analytics"],
    summary="Get click statistics",
    description="Get click statistics for a shortened URL",
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_url_stats(
    request: Request,
    slug: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ClickStatsResponse:
    """Get click statistics for a short URL."""
    from src.database.crud import get_click_stats_for_slug

    stats = await get_click_stats_for_slug(slug, session)
    return ClickStatsResponse(**stats)


# ============================================
# Legacy Routes (for backward compatibility)
# ============================================


@app.post("/short_url", response_model=ShortenUrlResponse, tags=["Legacy"])
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def legacy_create_short_url(
    request: Request,
    body: ShortenUrlRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ShortenUrlResponse:
    """Legacy endpoint for creating short URLs (use /api/v1/urls instead)."""
    # Redirect to new API logic
    long_url_str = str(body.long_url)

    existing_slug = await check_existing_url(long_url_str, session)
    if existing_slug:
        return ShortenUrlResponse(
            data=existing_slug,
            short_url=f"{request.base_url}{existing_slug}",
            long_url=long_url_str,
            custom_slug=False,
            expires_at=None,
        )

    try:
        slug, is_custom, expires_at = await generate_short_url(
            long_url_str,
            session,
            custom_slug=body.custom_slug,
            expires_in_days=body.expires_in_days,
        )
    except SlugAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    return ShortenUrlResponse(
        data=slug,
        short_url=f"{request.base_url}{slug}",
        long_url=long_url_str,
        custom_slug=is_custom,
        expires_at=expires_at,
    )


@app.get("/{slug}", tags=["Legacy"])
async def redirect_to_url(
    request: Request,
    slug: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RedirectResponse:
    """Redirect to the original URL and queue click analytics.

    Uses the cache-aside pattern (check cache first, then database):
    1. Check Redis cache for URL
    2. If cache hit: return URL and queue click event
    3. If cache miss: query PostgreSQL, cache result, queue click event
    4. Graceful degradation: if Redis fails, fallback to PostgreSQL only
    """
    long_url = None

    # Try to get from cache
    try:
        long_url = await get_cached_url(slug, settings)
        if long_url:
            # Cache hit - increment metrics
            from src.cache import increment_cache_hits

            await increment_cache_hits(settings)
    except redis.RedisError as e:
        logger.warning(f"Redis error on cache read, falling back to DB: {e}")

    # Cache miss or Redis error - query database
    if not long_url:
        try:
            # Cache miss - increment metrics
            from src.cache import increment_cache_misses

            await increment_cache_misses(settings)

            long_url = await get_url_by_slug(slug, session)

            # Cache the result for future requests
            if long_url:
                await cache_url(slug, long_url, settings)
        except Exception as e:
            logger.error(f"Error getting URL from database: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="URL not found or expired",
            )

    if not long_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found or expired",
        )

    # Get client info for analytics
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    referer = get_referer(request)

    # Queue click event for async processing (non-blocking)
    # Graceful degradation: if queue fails, still redirect the user
    try:
        # Get Redis connection for queue
        from arq import create_pool
        from arq.connections import RedisSettings

        redis_pool = await create_pool(
            RedisSettings(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                database=settings.redis_db,
            )
        )
        if redis_pool:
            from arq import enqueue_job  # type: ignore[attr-defined]

            await enqueue_job(
                redis_pool,
                "process_click_event",
                slug=slug,
                ip_address=ip_address,
                user_agent=user_agent,
                referer=referer,
            )
    except Exception as e:
        # Log error but don't fail the redirect
        logger.error(f"Failed to queue click event: {e}")

    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)
