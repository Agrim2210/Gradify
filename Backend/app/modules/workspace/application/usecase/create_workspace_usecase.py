from app.modules.workspace.domain.repositories.workspace_repo import WorkspaceRepo
from app.modules.workspace.domain.entities.workspace import Workspace as WorkspaceEntity
from app.infra.database.uow import uow_contract
from app.modules.workspace.application.services.slug_generator import SlugGenerator
from app.modules.workspace.application.dto.create_workspace_req import RequestCreateWorkspace
from app.modules.workspace.domain.entities.workspace_membership import WorkspaceMembership as Membership
from app.modules.workspace.domain.repositories.membership_repo import WorkspaceMembershipRepo
from app.modules.workspace.application.dto.response import ResponseCreateWorkspace


class CreateWorkspace:
    def __init__(self, workspace_repo: WorkspaceRepo, uow: uow_contract, slug_generator: SlugGenerator, membership_repo: WorkspaceMembershipRepo):
        self.workspace_repo = workspace_repo
        self.uow = uow
        self.membership_repo = membership_repo
        self.slug_generator = slug_generator

    async def execute(self, request: RequestCreateWorkspace):
        slug = await self.slug_generator.generate(request.name)
        workspace = WorkspaceEntity.create(name=request.name, slug=slug, description=request.description, updated_at=None)
        membership = Membership.create_owner(workspace_id=workspace.id, user_id=request.user_id)

        try:
            await self.workspace_repo.save(workspace)
            await self.uow.flush()
            await self.membership_repo.save(membership)
            await self.uow.commit()
            return ResponseCreateWorkspace(id=workspace.id, name=workspace.name, slug=workspace.slug)
        except Exception:
            await self.uow.rollback()
            raise
                

                