from alembic import op


revision = "c3e7a9b4d120"
down_revision = ("77da9e7b4f7e", "9a4c8d1e2f30")
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_workspace_membership_workspace_user",
        "workspace_membership",
        ["workspace_id", "user_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_workspace_membership_workspace_user",
        "workspace_membership",
        type_="unique",
    )
