from app.modules.workspace.domain.repositories.membership_repo import WorkspaceMembershipRepo
from uuid import UUID
from app.modules.workspace.application.dto.membership_response import ResponseMembership, WorkspaceItemDTO
from app.modules.workspace.domain.repositories.workspace_repo import WorkspaceRepo

class GetMembershipUseCase:
    def __init__(self, membership_repo: WorkspaceMembershipRepo, workspace_repo: WorkspaceRepo):
        self.membership_repo = membership_repo
        self.workspace_repo = workspace_repo

    async def execute(self, user_id: UUID, selected_slug: str | None = None) -> ResponseMembership | None:
        memberships = await self.membership_repo.list_by_user_id(user_id)
        if not memberships:
            return None

        workspace_ids = [m.workspace_id for m in memberships]
        workspaces = await self.workspace_repo.get_by_ids(workspace_ids)
        ws_by_id = {ws.id: ws for ws in workspaces}

        workspace_items: list[WorkspaceItemDTO] = []
        for m in memberships:
            ws = ws_by_id.get(m.workspace_id)
            if ws:
                role_str = m.role.value if hasattr(m.role, "value") else str(m.role)
                workspace_items.append(
                    WorkspaceItemDTO(
                        id=ws.id,
                        name=ws.name,
                        slug=ws.slug,
                        role=role_str,
                        description=ws.description,
                        created_at=ws.created_at,
                    )
                )

        if not workspace_items:
            return None

        active_item = None
        if selected_slug:
            active_item = next((w for w in workspace_items if w.slug == selected_slug), None)

        if not active_item:
            active_item = workspace_items[0]

        return ResponseMembership(
            workspace_name=active_item.name,
            slug=active_item.slug,
            role=active_item.role,
            workspaces=workspace_items,
        )

        
        
            