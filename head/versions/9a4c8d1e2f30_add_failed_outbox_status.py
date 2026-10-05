"""add FAILED to the PostgreSQL outbox status enum

Revision ID: 9a4c8d1e2f30
Revises: 27651acb1ed3
Create Date: 2026-09-14
"""
from typing import Sequence, Union

from alembic import op


revision: str = "9a4c8d1e2f30"
down_revision: Union[str, Sequence[str], None] = "27651acb1ed3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PostgreSQL requires ALTER TYPE ... ADD VALUE outside the migration transaction.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE status ADD VALUE IF NOT EXISTS 'FAILED'")


def downgrade() -> None:
    # PostgreSQL does not support removing an enum label without recreating the type.
    pass
