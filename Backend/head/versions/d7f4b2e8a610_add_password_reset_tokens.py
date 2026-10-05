from alembic import op
import sqlalchemy as sa

revision = "d7f4b2e8a610"
down_revision = "f2a8c6d9e410"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("password_reset_tokens", sa.Column("id", sa.UUID(), nullable=False), sa.Column("user_id", sa.UUID(), nullable=False), sa.Column("token_hash", sa.String(length=64), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("used_at", sa.DateTime(timezone=True), nullable=True), sa.ForeignKeyConstraint(["user_id"], ["users.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("token_hash"))

def downgrade() -> None:
    op.drop_table("password_reset_tokens")
