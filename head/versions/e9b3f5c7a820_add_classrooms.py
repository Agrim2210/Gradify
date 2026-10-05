from alembic import op
import sqlalchemy as sa

revision = "e9b3f5c7a820"
down_revision = "d7f4b2e8a610"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("classrooms", sa.Column("id", sa.UUID(), nullable=False), sa.Column("workspace_id", sa.UUID(), nullable=False), sa.Column("name", sa.String(length=100), nullable=False), sa.Column("created_by_user_id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(["workspace_id"], ["workspace.id"]), sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_table("classroom_memberships", sa.Column("id", sa.UUID(), nullable=False), sa.Column("classroom_id", sa.UUID(), nullable=False), sa.Column("user_id", sa.UUID(), nullable=False), sa.Column("role", sa.Enum("OWNER", "STUDENT", name="classroom_role"), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(["classroom_id"], ["classrooms.id"]), sa.ForeignKeyConstraint(["user_id"], ["users.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("classroom_id", "user_id", name="uq_classroom_membership_classroom_user"))
    op.create_table("classroom_invitations", sa.Column("id", sa.UUID(), nullable=False), sa.Column("classroom_id", sa.UUID(), nullable=False), sa.Column("email", sa.String(length=250), nullable=False), sa.Column("token_hash", sa.String(length=64), nullable=False), sa.Column("invited_by_user_id", sa.UUID(), nullable=False), sa.Column("status", sa.Enum("PENDING", "ACCEPTED", "EXPIRED", "REVOKED", name="invitation_status", create_type=False), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(["classroom_id"], ["classrooms.id"]), sa.ForeignKeyConstraint(["invited_by_user_id"], ["users.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("classroom_id", "email", name="uq_classroom_invitation_classroom_email"), sa.UniqueConstraint("token_hash"))

def downgrade() -> None:
    op.drop_table("classroom_invitations")
    op.drop_table("classroom_memberships")
    op.drop_table("classrooms")
