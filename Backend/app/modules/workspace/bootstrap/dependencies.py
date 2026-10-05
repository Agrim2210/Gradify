from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database.session import get_db
from app.infra.database.uow import uow_contract, uow_implementation
from app.modules.auth.application.outbox.outbox_repo import OutboxRepo
from app.modules.auth.bootstrap.dependencies import (
    get_password_hasher,
    get_token_provider,
    get_user_repo,
)
from app.modules.auth.domain.interface.password_hashing_repo import PasswordHasher
from app.modules.auth.domain.interface.user_repo import UserRepo
from app.modules.auth.infra.persistent.repositories.sqlalchemy_outbox_repository import SQLAlchemyOutboxRepository
from app.modules.workspace.application.services.get_workspace_context import GetWorkspaceContext
from app.modules.workspace.application.services.slug_generator import SlugGenerator
from app.modules.workspace.application.usecase.accept_invitation import AcceptInvitation
from app.modules.workspace.application.usecase.change_member_role import ChangeMemberRole
from app.modules.workspace.application.usecase.classroom import ClassroomService
from app.modules.workspace.application.usecase.create_workspace_usecase import CreateWorkspace
from app.modules.workspace.application.usecase.get_membership import GetMembershipUseCase
from app.modules.workspace.application.usecase.invite_member import InviteMember
from app.modules.workspace.domain.repositories.invitation_repo import WorkspaceInvitationRepo
from app.modules.workspace.domain.repositories.membership_repo import WorkspaceMembershipRepo
from app.modules.workspace.domain.repositories.workspace_repo import WorkspaceRepo
from app.modules.workspace.infra.database.repositories.invitation_repo import WorkspaceInvitationSQLRepo
from app.modules.workspace.infra.database.repositories.membership_repo import WorkspaceMembershipSQLRepo
from app.modules.workspace.infra.database.repositories.workspace_sql_repo import WorkspaceSQLREPO
from app.shared.application.security.token_provider import TokenProvider


def get_workspace_repo(session: AsyncSession = Depends(get_db)) -> WorkspaceRepo:
    return WorkspaceSQLREPO(session)


def get_membership_repo(session: AsyncSession = Depends(get_db)) -> WorkspaceMembershipRepo:
    return WorkspaceMembershipSQLRepo(session)


def get_invitation_repo(session: AsyncSession = Depends(get_db)) -> WorkspaceInvitationRepo:
    return WorkspaceInvitationSQLRepo(session)


def get_outbox_repo(session: AsyncSession = Depends(get_db)) -> OutboxRepo:
    return SQLAlchemyOutboxRepository(session)


def get_uow(session: AsyncSession = Depends(get_db)) -> uow_contract:
    return uow_implementation(session)


def get_slug_generator(workspace_repo: WorkspaceRepo = Depends(get_workspace_repo)) -> SlugGenerator:
    return SlugGenerator(workspace_repo=workspace_repo)


def get_create_workspace_usecase(
    workspace_repo: WorkspaceRepo = Depends(get_workspace_repo),
    uow: uow_contract = Depends(get_uow),
    membership_repo: WorkspaceMembershipRepo = Depends(get_membership_repo),
    slug_generator: SlugGenerator = Depends(get_slug_generator),
) -> CreateWorkspace:
    return CreateWorkspace(workspace_repo=workspace_repo, uow=uow, slug_generator=slug_generator, membership_repo=membership_repo)


def get_membership_usecase(
    membership_repo: WorkspaceMembershipRepo = Depends(get_membership_repo),
    workspace_repo: WorkspaceRepo = Depends(get_workspace_repo),
) -> GetMembershipUseCase:
    return GetMembershipUseCase(membership_repo=membership_repo, workspace_repo=workspace_repo)


def get_workspace_context_service(
    workspace_repo: WorkspaceRepo = Depends(get_workspace_repo),
    membership_repo: WorkspaceMembershipRepo = Depends(get_membership_repo),
) -> GetWorkspaceContext:
    return GetWorkspaceContext(workspace_repo=workspace_repo, membership_repo=membership_repo)


def get_invite_member_usecase(
    workspace_repo: WorkspaceRepo = Depends(get_workspace_repo),
    membership_repo: WorkspaceMembershipRepo = Depends(get_membership_repo),
    invitation_repo: WorkspaceInvitationRepo = Depends(get_invitation_repo),
    outbox_repo: OutboxRepo = Depends(get_outbox_repo),
    uow: uow_contract = Depends(get_uow),
) -> InviteMember:
    return InviteMember(workspace_repo, membership_repo, invitation_repo, outbox_repo, uow)


def get_accept_invitation_usecase(
    invitation_repo: WorkspaceInvitationRepo = Depends(get_invitation_repo),
    membership_repo: WorkspaceMembershipRepo = Depends(get_membership_repo),
    workspace_repo: WorkspaceRepo = Depends(get_workspace_repo),
    user_repo: UserRepo = Depends(get_user_repo),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_provider: TokenProvider = Depends(get_token_provider),
    uow: uow_contract = Depends(get_uow),
) -> AcceptInvitation:
    return AcceptInvitation(
        invitation_repo=invitation_repo,
        membership_repo=membership_repo,
        workspace_repo=workspace_repo,
        user_repo=user_repo,
        password_hasher=password_hasher,
        token_provider=token_provider,
        uow=uow,
    )


def get_change_member_role_usecase(
    workspace_repo: WorkspaceRepo = Depends(get_workspace_repo),
    membership_repo: WorkspaceMembershipRepo = Depends(get_membership_repo),
    uow: uow_contract = Depends(get_uow),
) -> ChangeMemberRole:
    return ChangeMemberRole(workspace_repo, membership_repo, uow)


def get_classroom_service(
    session: AsyncSession = Depends(get_db),
    outbox_repo: OutboxRepo = Depends(get_outbox_repo),
    uow: uow_contract = Depends(get_uow),
) -> ClassroomService:
    return ClassroomService(session, outbox_repo, uow)
