from dataclasses import dataclass

from app.modules.workspace.domain.enums.workspace_role import WorkspaceRole


@dataclass(frozen=True)
class InviteMemberCommand:
    email: str
    role: WorkspaceRole
