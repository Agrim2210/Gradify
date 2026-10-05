import hashlib
import secrets
from datetime import datetime, timezone, timedelta

from app.core.config import settings
from app.infra.database.uow import uow_contract
from app.modules.auth.application.dto.outbox_dto import Payload
from app.modules.auth.application.enums.outbox_enum import EventType
from app.modules.auth.application.outbox.outbox_event import OutBoxEvent
from app.modules.auth.application.outbox.outbox_repo import OutboxRepo
from app.modules.workspace.application.dto.invite_member import InviteMemberCommand
from app.modules.workspace.domain.entities.workspace_invitation import WorkspaceInvitation
from app.modules.workspace.domain.enums.invitation_status import InvitationStatus
from app.modules.workspace.domain.enums.workspace_role import WorkspaceRole
from app.modules.workspace.domain.enums.workspace_status import WorkspaceStatus
from app.modules.workspace.domain.exception.exception import WorkspaceAccessDenied, WorkspaceNotFound
from app.modules.workspace.domain.repositories.invitation_repo import WorkspaceInvitationRepo
from app.modules.workspace.domain.repositories.membership_repo import WorkspaceMembershipRepo
from app.modules.workspace.domain.repositories.workspace_repo import WorkspaceRepo


class InviteMember:
    def __init__(self, workspace_repo: WorkspaceRepo, membership_repo: WorkspaceMembershipRepo, invitation_repo: WorkspaceInvitationRepo, outbox_repo: OutboxRepo, uow: uow_contract):
        self.workspace_repo = workspace_repo
        self.membership_repo = membership_repo
        self.invitation_repo = invitation_repo
        self.outbox_repo = outbox_repo
        self.uow = uow

    async def execute(self, slug: str, requester_id, command: InviteMemberCommand) -> dict:
        workspace = await self.workspace_repo.get_by_slug(slug)
        if workspace is None or workspace.status != WorkspaceStatus.ACTIVE:
            raise WorkspaceNotFound()
        membership = await self.membership_repo.get_by_user_workspace(requester_id, workspace.id)
        if membership is None:
            raise WorkspaceAccessDenied()

        # Permission check:
        # OWNER can invite any role (TEACHER or STUDENT).
        # TEACHER can invite students to the workspace.
        if command.role == WorkspaceRole.STUDENT:
            if membership.role not in (WorkspaceRole.OWNER, WorkspaceRole.TEACHER):
                raise WorkspaceAccessDenied()
        else:
            if membership.role != WorkspaceRole.OWNER:
                raise WorkspaceAccessDenied()

        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        clean_email = command.email.strip().lower()

        # Handle re-invites or existing invitations
        existing = await self.invitation_repo.get_by_workspace_and_email(workspace.id, clean_email)
        if existing:
            existing.token_hash = token_hash
            existing.role = command.role
            existing.status = InvitationStatus.PENDING
            existing.expires_at = datetime.now(timezone.utc) + timedelta(days=7)
            existing.accepted_at = None
            invitation = existing
            await self.invitation_repo.update(invitation)
        else:
            invitation = WorkspaceInvitation.create(workspace.id, clean_email, command.role, token_hash, requester_id)
            await self.invitation_repo.save(invitation)

        role_str = command.role.value if hasattr(command.role, "value") else str(command.role)
        invitation_url = f"{settings.FRONTEND_URL.rstrip('/')}/?invite_token={token}&email={clean_email}&role={role_str}"
        event = OutBoxEvent.create(
            Payload(
                email=invitation.email,
                invitation_url=invitation_url,
                workspace_name=workspace.name,
                role=role_str,
            ),
            EventType.SEND_WORKSPACE_INVITATION,
        )
        self.outbox_repo.add(event)
        await self.uow.commit()

        return {
            "token": token,
            "invitation_url": invitation_url,
            "workspace_name": workspace.name,
            "role": command.role.value if hasattr(command.role, "value") else str(command.role),
            "email": clean_email,
        }
