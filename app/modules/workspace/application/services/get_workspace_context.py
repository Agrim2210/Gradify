from app.modules.auth.application.dto.current_user import CurrentUser
from app.modules.workspace.application.dto.workspace_context import WorkspaceContext
from app.modules.workspace.domain.enums.membership_status import MembershipStatus
from app.modules.workspace.domain.enums.workspace_status import WorkspaceStatus
from app.modules.workspace.domain.exception.exception import (
    WorkspaceAccessDenied,
    WorkspaceNotFound,
)
from app.modules.workspace.domain.repositories.workspace_repo import WorkspaceRepo
from app.modules.workspace.domain.repositories.membership_repo import (
    WorkspaceMembershipRepo,
)

class GetWorkspaceContext:

    def __init__(
        self,
        workspace_repo: WorkspaceRepo,
        membership_repo: WorkspaceMembershipRepo,
    ):
        self._workspace_repo = workspace_repo
        self._membership_repo = membership_repo

    async def execute(
        self,
        *,
        slug: str,
        current_user: CurrentUser,
    ) -> WorkspaceContext:

        workspace = await self._workspace_repo.get_by_slug(slug)

        if workspace is None or workspace.status != WorkspaceStatus.ACTIVE:
            raise WorkspaceNotFound()

        membership = await self._membership_repo.get_by_user_workspace(
            user_id=current_user.id,
            workspace_id=workspace.id,
        )

        if membership is None:
            raise WorkspaceAccessDenied()

        if membership.status != MembershipStatus.ACTIVE:
            raise WorkspaceAccessDenied()

        return WorkspaceContext(
            user_id=current_user.id,
            workspace_id=workspace.id,
            workspace_name=workspace.name,
            workspace_slug=workspace.slug,
            role=membership.role.value if hasattr(membership.role, "value") else str(membership.role),
            membership_status=membership.status,
        )
