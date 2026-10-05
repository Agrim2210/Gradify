from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.workspace.domain.entities.workspace_invitation import WorkspaceInvitation


class WorkspaceInvitationRepo(ABC):
    @abstractmethod
    async def save(self, invitation: WorkspaceInvitation) -> None:
        ...

    @abstractmethod
    async def get_by_token_hash(self, token_hash: str) -> WorkspaceInvitation | None:
        ...

    @abstractmethod
    async def get_by_workspace_and_email(self, workspace_id: UUID, email: str) -> WorkspaceInvitation | None:
        ...

    @abstractmethod
    async def update(self, invitation: WorkspaceInvitation) -> None:
        ...
