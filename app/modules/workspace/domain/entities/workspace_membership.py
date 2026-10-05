from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.modules.workspace.domain.enums.workspace_role import WorkspaceRole
from app.modules.workspace.domain.enums.membership_status import MembershipStatus


@dataclass
class WorkspaceMembership:
    id: UUID
    workspace_id: UUID
    user_id: UUID
    role: WorkspaceRole
    status: MembershipStatus
    joined_at: datetime
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create_owner(
        cls,
        *,
        workspace_id: UUID,
        user_id: UUID,
    ) -> "WorkspaceMembership":

        now = datetime.now(timezone.utc)

        return cls(
            id=uuid4(),
            workspace_id=workspace_id,
            user_id=user_id,
            role=WorkspaceRole.OWNER,
            status=MembershipStatus.ACTIVE,
            joined_at=now,
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def create_member(cls, workspace_id: UUID, user_id: UUID, role: WorkspaceRole) -> "WorkspaceMembership":
        now = datetime.now(timezone.utc)
        return cls(uuid4(), workspace_id, user_id, role, MembershipStatus.ACTIVE, now, now, now)

    def suspend(self):
        self.status = MembershipStatus.SUSPENDED

    def activate(self):
        self.status = MembershipStatus.ACTIVE

    def remove(self):
        self.status = MembershipStatus.REMOVED

    def promote_to_teacher(self):
        self.role = WorkspaceRole.TEACHER

    def make_owner(self):
        self.role = WorkspaceRole.OWNER

    def change_role(self, role: WorkspaceRole):
        self.role = role
        self.updated_at = datetime.now(timezone.utc)
