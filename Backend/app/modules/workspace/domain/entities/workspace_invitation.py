from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from app.modules.workspace.domain.enums.invitation_status import InvitationStatus
from app.modules.workspace.domain.enums.workspace_role import WorkspaceRole


@dataclass
class WorkspaceInvitation:
    id: UUID
    workspace_id: UUID
    email: str
    role: WorkspaceRole
    token_hash: str
    invited_by_user_id: UUID
    status: InvitationStatus
    expires_at: datetime
    accepted_at: datetime | None
    created_at: datetime

    @classmethod
    def create(cls, workspace_id: UUID, email: str, role: WorkspaceRole, token_hash: str, invited_by_user_id: UUID) -> "WorkspaceInvitation":
        now = datetime.now(timezone.utc)
        return cls(uuid4(), workspace_id, email.lower(), role, token_hash, invited_by_user_id, InvitationStatus.PENDING, now + timedelta(days=7), None, now)

    def accept(self) -> None:
        self.status = InvitationStatus.ACCEPTED
        self.accepted_at = datetime.now(timezone.utc)
