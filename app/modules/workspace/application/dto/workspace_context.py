from dataclasses import dataclass
from uuid import UUID

from app.modules.workspace.domain.enums.workspace_role import WorkspaceRole
from app.modules.workspace.domain.enums.membership_status import MembershipStatus


@dataclass(frozen=True)
class WorkspaceContext:
    user_id: UUID

    workspace_id: UUID
    workspace_name: str
    workspace_slug: str

    role: WorkspaceRole
    membership_status: MembershipStatus