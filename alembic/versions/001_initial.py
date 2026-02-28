"""Initial schema creation."""

__revision_id__ = "001_initial"
__revises__ = None
__create_date__ = "2026-02-20"

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create initial database schema."""
    # Create short_urls table
    op.create_table(
        "short_urls",
        sa.Column("slug", sa.String(length=12), nullable=False),
        sa.Column("long_url", sa.Text(), nullable=False),
        sa.Column("custom_slug", sa.Boolean(), nullable=False, default=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("slug"),
    )
    op.create_index(op.f("ix_short_urls_slug"), "short_urls", ["slug"], unique=False)
    op.create_index(
        op.f("ix_short_urls_long_url"), "short_urls", ["long_url"], unique=False
    )
    op.create_index(
        op.f("ix_short_urls_expires_at"), "short_urls", ["expires_at"], unique=False
    )

    # Create clicks table
    op.create_table(
        "clicks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("slug", sa.String(length=12), nullable=False),
        sa.Column(
            "clicked_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("referer", sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(["slug"], ["short_urls.slug"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_clicks_slug"), "clicks", ["slug"], unique=False)
    op.create_index(
        op.f("ix_clicks_clicked_at"), "clicks", ["clicked_at"], unique=False
    )


def downgrade() -> None:
    """Drop initial database schema."""
    op.drop_table("clicks")
    op.drop_index(op.f("ix_short_urls_expires_at"), table_name="short_urls")
    op.drop_index(op.f("ix_short_urls_long_url"), table_name="short_urls")
    op.drop_index(op.f("ix_short_urls_slug"), table_name="short_urls")
    op.drop_table("short_urls")
