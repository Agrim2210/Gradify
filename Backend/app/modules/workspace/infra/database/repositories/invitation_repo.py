from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.workspace.domain.entities.workspace_invitation import WorkspaceInvitation
from app.modules.workspace.domain.repositories.invitation_repo import WorkspaceInvitationRepo
from app.modules.workspace.infra.database.invitation_sql import WorkspaceInvitationModel


class WorkspaceInvitationSQLRepo(WorkspaceInvitationRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, invitation: WorkspaceInvitation) -> None:
        self.session.add(self._to_model(invitation))

    async def get_by_token_hash(self, token_hash: str) -> WorkspaceInvitation | None:
        result = await self.session.execute(select(WorkspaceInvitationModel).where(WorkspaceInvitationModel.token_hash == token_hash))
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_workspace_and_email(self, workspace_id: UUID, email: str) -> WorkspaceInvitation | None:
        result = await self.session.execute(
            select(WorkspaceInvitationModel).where(
                WorkspaceInvitationModel.workspace_id == workspace_id,
                WorkspaceInvitationModel.email == email.lower(),
            )
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def update(self, invitation: WorkspaceInvitation) -> None:
        model = await self.session.get(WorkspaceInvitationModel, invitation.id)
        if model:
            model.token_hash = invitation.token_hash
            model.role = invitation.role
            model.status = invitation.status
            model.expires_at = invitation.expires_at
            model.accepted_at = invitation.accepted_at

    @staticmethod
    def _to_model(invitation: WorkspaceInvitation) -> WorkspaceInvitationModel:
        return WorkspaceInvitationModel(**invitation.__dict__)

    @staticmethod
    def _to_domain(model: WorkspaceInvitationModel) -> WorkspaceInvitation:
        return WorkspaceInvitation(**{column.name: getattr(model, column.name) for column in model.__table__.columns})
