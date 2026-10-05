"""add verified_at to users

Revision ID: b18a6d9e0f21
Revises: 81fc82e14fb5
Create Date: 2026-07-29 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b18a6d9e0f21"
down_revision: Union[str, Sequence[str], None] = "81fc82e14fb5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "verified_at")
