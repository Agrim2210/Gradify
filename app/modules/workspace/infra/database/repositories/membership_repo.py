from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.workspace.domain.entities.workspace_membership import (
    WorkspaceMembership,
)
from app.modules.workspace.domain.repositories.membership_repo import (
    WorkspaceMembershipRepo,
)
from app.modules.workspace.infra.database.membership_sql import (
    WorkspaceMembershipModel,
)
from app.modules.workspace.domain.enums.membership_status import MembershipStatus
from app.modules.auth.infra.persistent.models.models import UserModel


class WorkspaceMembershipSQLRepo(WorkspaceMembershipRepo):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(
        self,
        membership: WorkspaceMembership,
    ) -> None:

        model = WorkspaceMembershipModel(
            id=membership.id,
            workspace_id=membership.workspace_id,
            user_id=membership.user_id,
            role=membership.role,
            status=membership.status,
            joined_at=membership.joined_at,
            created_at=membership.created_at,
            updated_at=membership.updated_at,
        )

        self.session.add(model)

    async def update(
        self,
        membership: WorkspaceMembership,
    ) -> None:
        model = await self.session.get(
            WorkspaceMembershipModel,
            membership.id,
        )
        if model is not None:
            model.role = membership.role
            model.status = membership.status
            model.updated_at = membership.updated_at

    async def get_by_id(
        self,
        membership_id: UUID,
    ) -> WorkspaceMembership | None:

        model = await self.session.get(
            WorkspaceMembershipModel,
            membership_id,
        )

        if model is None:
            return None

        return self._to_domain(model)

    async def get_by_user_workspace(
        self,
        user_id: UUID,
        workspace_id: UUID,
    ) -> WorkspaceMembership | None:

        stmt = (
            select(WorkspaceMembershipModel)
            .where(
                WorkspaceMembershipModel.user_id == user_id,
                WorkspaceMembershipModel.workspace_id == workspace_id,
            )
        )

        result = await self.session.execute(stmt)

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def exists(
        self,
        user_id: UUID,
        workspace_id: UUID,
    ) -> bool:

        stmt = (
            select(WorkspaceMembershipModel)
            .where(
                WorkspaceMembershipModel.user_id == user_id,
                WorkspaceMembershipModel.workspace_id == workspace_id,
            )
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none() is not None

    async def list_workspace_members(self, workspace_id: UUID) -> list[dict]:
        stmt = (
            select(WorkspaceMembershipModel, UserModel.email)
            .join(UserModel, WorkspaceMembershipModel.user_id == UserModel.id)
            .where(
                WorkspaceMembershipModel.workspace_id == workspace_id,
                WorkspaceMembershipModel.status == MembershipStatus.ACTIVE,
            )
            .order_by(WorkspaceMembershipModel.joined_at.asc())
        )
        result = await self.session.execute(stmt)
        members = []
        for model, email in result.all():
            members.append({
                "membership_id": str(model.id),
                "user_id": str(model.user_id),
                "email": email,
                "role": model.role.value if hasattr(model.role, "value") else str(model.role),
                "status": model.status.value if hasattr(model.status, "value") else str(model.status),
                "joined_at": model.joined_at.isoformat() if model.joined_at else None,
            })
        return members

    @staticmethod
    def _to_domain(
        model: WorkspaceMembershipModel,
    ) -> WorkspaceMembership:

        return WorkspaceMembership(
            id=model.id,
            workspace_id=model.workspace_id,
            user_id=model.user_id,
            role=model.role,
            status=model.status,
            joined_at=model.joined_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_user_id(self, user_id: UUID):
        stmt = (
            select(WorkspaceMembershipModel)
            .where(WorkspaceMembershipModel.user_id == user_id)
            .order_by(WorkspaceMembershipModel.created_at.desc())
        )
        execute = await self.session.execute(stmt)
        workspaces = execute.scalars().first()
        if not workspaces:
            return None
        return self._to_domain(workspaces)

    async def list_by_user_id(self, user_id: UUID) -> list[WorkspaceMembership]:
        stmt = (
            select(WorkspaceMembershipModel)
            .where(WorkspaceMembershipModel.user_id == user_id)
            .order_by(WorkspaceMembershipModel.created_at.desc())
        )
        execute = await self.session.execute(stmt)
        models = execute.scalars().all()
        return [self._to_domain(m) for m in models]

