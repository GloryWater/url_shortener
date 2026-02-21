"""Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

# ============================================
# Request Schemas
# ============================================


class ShortenUrlRequest(BaseModel):
    """Short URL creation request schema."""

    long_url: HttpUrl = Field(
        ...,
        description="Long URL to shorten",
        examples=["https://example.com/very/long/url"],
    )
    custom_slug: str | None = Field(
        None,
        description="Optional custom slug (alphanumeric, 4-12 chars)",
        pattern=r"^[a-zA-Z0-9]{4,12}$",
        examples=["mylink"],
    )
    expires_in_days: int | None = Field(
        None,
        description="Optional expiration in days (1-365)",
        ge=1,
        le=365,
        examples=[30],
    )


class DeleteUrlRequest(BaseModel):
    """Short URL deletion request schema (for API consistency, though DELETE uses path params)."""

    pass


# ============================================
# Response Schemas
# ============================================


class ShortenUrlResponse(BaseModel):
    """Short URL creation response schema."""

    data: str = Field(..., description="Generated or custom slug")
    short_url: str = Field(..., description="Full short URL")
    long_url: str = Field(..., description="Original long URL")
    custom_slug: bool = Field(default=False, description="Whether custom slug was used")
    expires_at: datetime | None = Field(
        None,
        description="Expiration datetime (if set)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "data": "aB3xY9",
                    "short_url": "http://localhost:8000/aB3xY9",
                    "long_url": "https://example.com",
                    "custom_slug": False,
                    "expires_at": None,
                }
            ]
        }
    )


class UrlInfoResponse(BaseModel):
    """Detailed URL information response schema."""

    slug: str = Field(..., description="Short URL slug")
    long_url: str = Field(..., description="Original long URL")
    custom_slug: bool = Field(..., description="Whether custom slug was used")
    expires_at: datetime | None = Field(None, description="Expiration datetime")
    created_at: datetime = Field(..., description="Creation datetime")
    updated_at: datetime = Field(..., description="Last update datetime")
    click_count: int = Field(..., description="Total number of clicks")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "slug": "aB3xY9",
                    "long_url": "https://example.com",
                    "custom_slug": False,
                    "expires_at": None,
                    "created_at": "2026-02-20T12:00:00Z",
                    "updated_at": "2026-02-20T12:00:00Z",
                    "click_count": 42,
                }
            ]
        },
    )


class UrlListResponse(BaseModel):
    """Paginated URL list response schema."""

    items: list[UrlInfoResponse] = Field(..., description="List of URLs")
    total: int = Field(..., description="Total number of URLs")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "items": [],
                    "total": 100,
                    "page": 1,
                    "limit": 20,
                    "pages": 5,
                }
            ]
        }
    )


class ClickStatsResponse(BaseModel):
    """Click statistics response schema."""

    total_clicks: int = Field(..., description="Total number of clicks")
    last_click: datetime | None = Field(
        None,
        description="Datetime of the last click",
    )
    unique_ips: int = Field(..., description="Number of unique IP addresses")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "total_clicks": 150,
                    "last_click": "2026-02-20T15:30:00Z",
                    "unique_ips": 42,
                }
            ]
        }
    )


class DeleteResponse(BaseModel):
    """URL deletion response schema."""

    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Status message")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "message": "URL successfully deleted",
                }
            ]
        }
    )


# ============================================
# Error Schemas
# ============================================


class ErrorResponse(BaseModel):
    """Error response schema."""

    detail: str = Field(..., description="Error description")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"detail": "URL not found"},
                {"detail": "Invalid URL format"},
            ]
        }
    )


class ValidationErrorDetail(BaseModel):
    """Validation error details."""

    loc: list[str | int] = Field(..., description="Location of the error")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class ValidationErrorResponse(BaseModel):
    """Validation error response schema."""

    detail: list[ValidationErrorDetail] = Field(
        ...,
        description="List of validation errors",
    )


# ============================================
# Health Check Schemas
# ============================================


class HealthResponse(BaseModel):
    """Health check endpoint response schema."""

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="Application version")
    database: str = Field(..., description="Database connection status")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "status": "healthy",
                    "version": "0.3.0",
                    "database": "connected",
                }
            ]
        }
    )
