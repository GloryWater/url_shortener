"""SQLAlchemy models for the URL shortener application."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class ShortURL(Base):
    """Model for storing shortened URLs."""

    __tablename__ = "short_urls"

    slug: Mapped[str] = mapped_column(
        String(12),
        primary_key=True,
        index=True,
    )
    long_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True,
    )
    custom_slug: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship to clicks
    clicks: Mapped[list["Click"]] = relationship(
        "Click",
        back_populates="short_url",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def is_expired(self) -> bool:
        """Check if the URL has expired."""
        if self.expires_at is None:
            return False
        now = datetime.now(UTC)
        expires = self.expires_at
        # Ensure both datetimes are timezone-aware
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)
        return now > expires


class Click(Base):
    """Model for tracking URL clicks (analytics)."""

    __tablename__ = "clicks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    slug: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("short_urls.slug", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),  # IPv6 max length
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )
    referer: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )

    # Relationship to short URL
    short_url: Mapped["ShortURL"] = relationship(
        "ShortURL",
        back_populates="clicks",
    )
