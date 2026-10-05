from uuid import UUID

from app.infra.database.uow import uow_contract
from app.modules.workspace.domain.enums.workspace_role import WorkspaceRole
from app.modules.workspace.domain.enums.workspace_status import WorkspaceStatus
from app.modules.workspace.domain.exception.exception import WorkspaceAccessDenied, WorkspaceNotFound
from app.modules.workspace.domain.repositories.membership_repo import WorkspaceMembershipRepo
from app.modules.workspace.domain.repositories.workspace_repo import WorkspaceRepo


class ChangeMemberRole:
    def __init__(self, workspace_repo: WorkspaceRepo, membership_repo: WorkspaceMembershipRepo, uow: uow_contract):
        self.workspace_repo = workspace_repo
        self.membership_repo = membership_repo
        self.uow = uow

    async def execute(self, slug: str, requester_id: UUID, target_user_id: UUID, new_role: WorkspaceRole) -> dict:
        workspace = await self.workspace_repo.get_by_slug(slug)
        if workspace is None or workspace.status != WorkspaceStatus.ACTIVE:
            raise WorkspaceNotFound()

        requester_membership = await self.membership_repo.get_by_user_workspace(requester_id, workspace.id)
        if requester_membership is None or requester_membership.role != WorkspaceRole.OWNER:
            raise WorkspaceAccessDenied()

        target_membership = await self.membership_repo.get_by_user_workspace(target_user_id, workspace.id)
        if target_membership is None:
            raise WorkspaceNotFound()

        target_membership.change_role(new_role)
        try:
            await self.membership_repo.update(target_membership)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

        return {
            "user_id": str(target_user_id),
            "workspace_id": str(workspace.id),
            "role": new_role.value if hasattr(new_role, "value") else str(new_role),
        }
