"""Add users table and update short_urls, clicks."""

__revision_id__ = "002_add_users"
__revises__ = "001_initial"
__create_date__ = "2026-02-21"

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_add_users"
down_revision: str | None = "001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add users table and update related tables."""
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, default=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # Add owner_id column to short_urls
    op.add_column(
        "short_urls",
        sa.Column("owner_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_short_urls_owner_id_users",
        "short_urls",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        op.f("ix_short_urls_owner_id"), "short_urls", ["owner_id"], unique=False
    )

    # Add enriched data columns to clicks
    op.add_column(
        "clicks",
        sa.Column("country", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "clicks",
        sa.Column("city", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "clicks",
        sa.Column("browser", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "clicks",
        sa.Column("os", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "clicks",
        sa.Column("device", sa.String(length=100), nullable=True),
    )


def downgrade() -> None:
    """Revert users table and related changes."""
    # Remove enriched data columns from clicks
    op.drop_column("clicks", "device")
    op.drop_column("clicks", "os")
    op.drop_column("clicks", "browser")
    op.drop_column("clicks", "city")
    op.drop_column("clicks", "country")

    # Remove owner_id from short_urls
    op.drop_index(op.f("ix_short_urls_owner_id"), table_name="short_urls")
    op.drop_constraint(
        "fk_short_urls_owner_id_users",
        "short_urls",
        type_="foreignkey",
    )
    op.drop_column("short_urls", "owner_id")

    # Drop users table
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
