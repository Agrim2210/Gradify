from fastapi import Depends, Path

from app.modules.auth.bootstrap.dependencies import get_current_user
from app.modules.auth.application.dto.current_user import CurrentUser

from app.modules.workspace.application.dto.workspace_context import WorkspaceContext

from app.modules.workspace.application.services.get_workspace_context import (
    GetWorkspaceContext,
)

from app.modules.workspace.bootstrap.dependencies import get_workspace_context_service


async def get_workspace_context(
    slug: str = Path(...),
    current_user: CurrentUser = Depends(get_current_user),
    service: GetWorkspaceContext = Depends(get_workspace_context_service),
) -> WorkspaceContext:

    return await service.execute(
        slug=slug,
        current_user=current_user,
    )