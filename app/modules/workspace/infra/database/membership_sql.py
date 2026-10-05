from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, UUID, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.database.base import Base
from app.modules.workspace.domain.enums.workspace_role import WorkspaceRole
from app.modules.workspace.domain.enums.membership_status import MembershipStatus
from app.modules.workspace.infra.database.models import WorkspaceModel

class WorkspaceMembershipModel(Base):
    __tablename__ = "workspace_membership"
    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_membership_workspace_user"),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspace.id"),
        nullable=False,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    role: Mapped[WorkspaceRole] = mapped_column(
        Enum(WorkspaceRole, name="workspace_role"),
        nullable=False,
    )

    status: Mapped[MembershipStatus] = mapped_column(
        Enum(MembershipStatus, name="membership_status"),
        nullable=False,
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
