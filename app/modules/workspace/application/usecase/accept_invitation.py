import hashlib
from datetime import datetime, timezone

from app.infra.database.uow import uow_contract
from app.modules.auth.domain.entities.user_entity import User
from app.modules.auth.domain.interface.password_hashing_repo import PasswordHasher
from app.modules.auth.domain.interface.user_repo import UserRepo
from app.modules.workspace.domain.entities.workspace_membership import WorkspaceMembership
from app.modules.workspace.domain.enums.invitation_status import InvitationStatus
from app.modules.workspace.domain.enums.membership_status import MembershipStatus
from app.modules.workspace.domain.exception.exception import InvitationExpired, InvitationNotFound
from app.modules.workspace.domain.repositories.invitation_repo import WorkspaceInvitationRepo
from app.modules.workspace.domain.repositories.membership_repo import WorkspaceMembershipRepo
from app.modules.workspace.domain.repositories.workspace_repo import WorkspaceRepo
from app.shared.application.security.token_provider import TokenProvider


class AcceptInvitation:
    def __init__(
        self,
        invitation_repo: WorkspaceInvitationRepo,
        membership_repo: WorkspaceMembershipRepo,
        workspace_repo: WorkspaceRepo,
        user_repo: UserRepo,
        password_hasher: PasswordHasher,
        token_provider: TokenProvider,
        uow: uow_contract,
    ):
        self.invitation_repo = invitation_repo
        self.membership_repo = membership_repo
        self.workspace_repo = workspace_repo
        self.user_repo = user_repo
        self.password_hasher = password_hasher
        self.token_provider = token_provider
        self.uow = uow

    async def execute(self, token: str, password: str) -> dict:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        invitation = await self.invitation_repo.get_by_token_hash(token_hash)
        if invitation is None:
            raise InvitationNotFound()
        if invitation.status != InvitationStatus.PENDING or invitation.expires_at <= datetime.now(timezone.utc):
            raise InvitationExpired()

        email = invitation.email.strip().lower()
        now = datetime.now(timezone.utc)
        hashed_password = self.password_hasher.create_hash(password)

        # 1. Ensure user exists and password is set
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user is None:
            user = User.create(email=email, password_hash=hashed_password, created_at=now)
            self.user_repo.add(user)
        else:
            user = existing_user
            user.change_password(hashed_password)
            await self.user_repo.update(user)

        # 2. Add or update Workspace Membership
        existing_membership = await self.membership_repo.get_by_user_workspace(user.id, invitation.workspace_id)
        if existing_membership is None:
            membership = WorkspaceMembership.create_member(invitation.workspace_id, user.id, invitation.role)
            await self.membership_repo.save(membership)
        else:
            existing_membership.role = invitation.role
            existing_membership.status = MembershipStatus.ACTIVE
            await self.membership_repo.update(existing_membership)

        # 3. Accept invitation
        invitation.accept()
        await self.invitation_repo.update(invitation)

        try:
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

        # 4. Generate Auth Tokens for seamless immediate sign-in
        access_token = self.token_provider.issue_access_token(user.id)
        refresh_token = self.token_provider.issue_refresh_token(user.id)

        workspace = await self.workspace_repo.get_by_id(invitation.workspace_id)

        return {
            "message": "Invitation accepted successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
            },
            "workspace": {
                "id": str(workspace.id) if workspace else str(invitation.workspace_id),
                "name": workspace.name if workspace else "Academic Workspace",
                "slug": workspace.slug if workspace else "workspace",
                "role": invitation.role.value if hasattr(invitation.role, "value") else str(invitation.role),
            },
        }
