from alembic import op
import sqlalchemy as sa


revision = "f2a8c6d9e410"
down_revision = "c3e7a9b4d120"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workspace_invitations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=250), nullable=False),
        sa.Column("role", sa.Enum("OWNER", "TEACHER", "STUDENT", name="workspace_role", create_type=False), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("invited_by_user_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.Enum("PENDING", "ACCEPTED", "EXPIRED", "REVOKED", name="invitation_status"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspace.id"]),
        sa.ForeignKeyConstraint(["invited_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "email", name="uq_workspace_invitation_workspace_email"),
        sa.UniqueConstraint("token_hash"),
    )
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE eventtype ADD VALUE IF NOT EXISTS 'SEND_WORKSPACE_INVITATION'")


def downgrade() -> None:
    op.drop_table("workspace_invitations")
