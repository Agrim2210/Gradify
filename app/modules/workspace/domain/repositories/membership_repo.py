from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.workspace.domain.entities.workspace_membership import (
    WorkspaceMembership,
)


class WorkspaceMembershipRepo(ABC):

    @abstractmethod
    async def save(self, membership: WorkspaceMembership) -> None:
        ...

    @abstractmethod
    async def update(self, membership: WorkspaceMembership) -> None:
        ...

    @abstractmethod
    async def get_by_id(
        self,
        membership_id: UUID,
    ) -> WorkspaceMembership | None:
        ...

    @abstractmethod
    async def get_by_user_workspace(
        self,
        user_id: UUID,
        workspace_id: UUID,
    ) -> WorkspaceMembership | None:
        ...

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> WorkspaceMembership | None:
        ...

    @abstractmethod
    async def list_by_user_id(self, user_id: UUID) -> list[WorkspaceMembership]:
        ...

    @abstractmethod
    async def exists(
        self,
        user_id: UUID,
        workspace_id: UUID,
    ) -> bool:
        ...

    @abstractmethod
    async def list_workspace_members(self, workspace_id: UUID) -> list[dict]:
        ...
