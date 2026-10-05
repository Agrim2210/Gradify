import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.workspace.domain.enums.classroom_role import ClassroomRole
from app.modules.workspace.domain.enums.invitation_status import InvitationStatus
from app.modules.workspace.domain.enums.workspace_role import WorkspaceRole
from app.modules.workspace.domain.exception.exception import (
    WorkspaceAccessDenied,
    WorkspaceNotFound,
    InvitationEmailMismatch,
    InvitationExpired,
    InvitationNotFound,
    MembershipAlreadyExists,
)
from app.modules.workspace.infra.database.classroom_models import (
    ClassroomInvitationModel,
    ClassroomMembershipModel,
    ClassroomModel,
)


class ClassroomService:
    def __init__(self, session: AsyncSession, outbox_repo, uow):
        self.session = session
        self.outbox_repo = outbox_repo
        self.uow = uow

    async def create(self, workspace, user_id, name, assigned_teacher_id=None):
        from app.modules.workspace.infra.database.repositories.membership_repo import WorkspaceMembershipSQLRepo
        membership = await WorkspaceMembershipSQLRepo(self.session).get_by_user_workspace(user_id, workspace.id)
        if membership is None or membership.role not in {WorkspaceRole.OWNER, WorkspaceRole.TEACHER}:
            raise WorkspaceAccessDenied()

        effective_teacher_id = None
        if membership.role == WorkspaceRole.TEACHER:
            # Teacher creating their own classroom
            effective_teacher_id = user_id
        elif membership.role == WorkspaceRole.OWNER:
            # Admin creating classroom — can optionally assign to a teacher
            if assigned_teacher_id:
                t_mem = await WorkspaceMembershipSQLRepo(self.session).get_by_user_workspace(assigned_teacher_id, workspace.id)
                if t_mem and t_mem.role in {WorkspaceRole.TEACHER, WorkspaceRole.OWNER}:
                    effective_teacher_id = assigned_teacher_id
                else:
                    effective_teacher_id = None

        now = datetime.now(timezone.utc)
        classroom = ClassroomModel(
            id=uuid4(),
            workspace_id=workspace.id,
            name=name,
            created_by_user_id=user_id,
            assigned_teacher_id=effective_teacher_id,
            created_at=now,
        )
        self.session.add(classroom)
        await self.session.flush()

        # Add creator membership
        self.session.add(
            ClassroomMembershipModel(
                id=uuid4(),
                classroom_id=classroom.id,
                user_id=user_id,
                role=ClassroomRole.OWNER,
                roll_number=None,
                created_at=now,
            )
        )

        # If assigned to a teacher different from creator, also give them classroom owner status
        if effective_teacher_id and effective_teacher_id != user_id:
            self.session.add(
                ClassroomMembershipModel(
                    id=uuid4(),
                    classroom_id=classroom.id,
                    user_id=effective_teacher_id,
                    role=ClassroomRole.OWNER,
                    roll_number=None,
                    created_at=now,
                )
            )

        await self.uow.commit()
        return classroom

    async def list_classrooms(self, workspace_id, user_id):
        """Return classrooms in a workspace.
        - Teachers can ONLY see classrooms assigned to them or created by them.
        - Workspace Head (OWNER) and Students can see all classrooms in the workspace.
        """
        from app.modules.workspace.infra.database.repositories.membership_repo import WorkspaceMembershipSQLRepo
        membership = await WorkspaceMembershipSQLRepo(self.session).get_by_user_workspace(user_id, workspace_id)
        if membership is None:
            raise WorkspaceAccessDenied()

        if membership.role == WorkspaceRole.TEACHER:
            from sqlalchemy import or_, exists
            has_owner_membership = exists().where(
                ClassroomMembershipModel.classroom_id == ClassroomModel.id,
                ClassroomMembershipModel.user_id == user_id,
                ClassroomMembershipModel.role == ClassroomRole.OWNER,
            )
            query = (
                select(ClassroomModel)
                .where(
                    ClassroomModel.workspace_id == workspace_id,
                    or_(
                        ClassroomModel.created_by_user_id == user_id,
                        ClassroomModel.assigned_teacher_id == user_id,
                        has_owner_membership,
                    ),
                )
                .order_by(ClassroomModel.created_at.asc())
            )
        else:
            query = select(ClassroomModel).where(ClassroomModel.workspace_id == workspace_id).order_by(ClassroomModel.created_at.asc())

        rows = (await self.session.execute(query)).scalars().all()
        return rows

    async def invite_student(self, classroom_id, requester_id, email):
        membership = (
            await self.session.execute(
                select(ClassroomMembershipModel).where(
                    ClassroomMembershipModel.classroom_id == classroom_id,
                    ClassroomMembershipModel.user_id == requester_id,
                )
            )
        ).scalar_one_or_none()
        if membership is None or membership.role != ClassroomRole.OWNER:
            raise WorkspaceAccessDenied()
        classroom = await self.session.get(ClassroomModel, classroom_id)
        if classroom is None:
            raise WorkspaceNotFound()

        # Check if already invited — re-invite by resetting token
        existing = (
            await self.session.execute(
                select(ClassroomInvitationModel).where(
                    ClassroomInvitationModel.classroom_id == classroom_id,
                    ClassroomInvitationModel.email == email.lower(),
                )
            )
        ).scalar_one_or_none()

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        now = datetime.now(timezone.utc)
        invitation_url = (
            f"{settings.FRONTEND_URL.rstrip('/')}/"
            f"?classroom_invite_token={raw_token}&email={email.lower()}"
        )

        if existing is not None:
            existing.token_hash = token_hash
            existing.status = InvitationStatus.PENDING
            existing.expires_at = now + timedelta(days=7)
            existing.accepted_at = None
        else:
            invitation = ClassroomInvitationModel(
                id=uuid4(),
                classroom_id=classroom.id,
                email=email.lower(),
                token_hash=token_hash,
                invited_by_user_id=requester_id,
                status=InvitationStatus.PENDING,
                expires_at=now + timedelta(days=7),
                accepted_at=None,
                created_at=now,
            )
            self.session.add(invitation)

        await self.uow.commit()

        return {
            "email": email.lower(),
            "classroom_name": classroom.name,
            "invitation_url": invitation_url,
        }

    async def accept(self, raw_token: str, password: str, roll_number: str):
        """Public endpoint: accept classroom invitation, create user if needed, issue JWT."""
        from app.modules.auth.infra.security.argon2_password_hasher import Argon2PasswordHasher
        from app.modules.auth.infra.persistent.models.models import UserModel
        from app.shared.infra.security.jwt_token_provider import JWTTokenProvider

        invitation = (
            await self.session.execute(
                select(ClassroomInvitationModel).where(
                    ClassroomInvitationModel.token_hash == hashlib.sha256(raw_token.encode()).hexdigest()
                )
            )
        ).scalar_one_or_none()
        if invitation is None:
            raise InvitationNotFound()
        if invitation.status != InvitationStatus.PENDING or invitation.expires_at <= datetime.now(timezone.utc):
            raise InvitationExpired()

        # Provision or fetch user
        user = (
            await self.session.execute(select(UserModel).where(UserModel.email == invitation.email))
        ).scalar_one_or_none()

        hasher = Argon2PasswordHasher()
        now = datetime.now(timezone.utc)
        if user is None:
            user = UserModel(
                id=uuid4(),
                email=invitation.email,
                password_hash=hasher.create_hash(password),
                is_active=True,
                verified_at=now,
            )
            self.session.add(user)
            await self.session.flush()
        else:
            # Update password for returning invite links
            user.password_hash = hasher.create_hash(password)

        # Check if already a member
        exists = (
            await self.session.execute(
                select(ClassroomMembershipModel.id).where(
                    ClassroomMembershipModel.classroom_id == invitation.classroom_id,
                    ClassroomMembershipModel.user_id == user.id,
                )
            )
        ).scalar_one_or_none()

        if not exists:
            self.session.add(
                ClassroomMembershipModel(
                    id=uuid4(),
                    classroom_id=invitation.classroom_id,
                    user_id=user.id,
                    role=ClassroomRole.STUDENT,
                    roll_number=roll_number,
                    created_at=now,
                )
            )

        # Also ensure workspace membership exists
        classroom = await self.session.get(ClassroomModel, invitation.classroom_id)
        if classroom is not None:
            from app.modules.workspace.infra.database.membership_sql import WorkspaceMembershipModel
            from app.modules.workspace.domain.enums.membership_status import MembershipStatus
            ws_exists = (
                await self.session.execute(
                    select(WorkspaceMembershipModel.id).where(
                        WorkspaceMembershipModel.workspace_id == classroom.workspace_id,
                        WorkspaceMembershipModel.user_id == user.id,
                    )
                )
            ).scalar_one_or_none()
            if not ws_exists:
                self.session.add(
                    WorkspaceMembershipModel(
                        id=uuid4(),
                        workspace_id=classroom.workspace_id,
                        user_id=user.id,
                        role=WorkspaceRole.STUDENT,
                        status=MembershipStatus.ACTIVE,
                        joined_at=now,
                        created_at=now,
                        updated_at=now,
                    )
                )

        invitation.status = InvitationStatus.ACCEPTED
        invitation.accepted_at = now
        await self.uow.commit()

        from app.core.jwt_setting import JWTSettings
        token_provider = JWTTokenProvider(JWTSettings())
        access_token = token_provider.issue_access_token(user.id)
        refresh_token = token_provider.issue_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": str(user.id),
            "email": user.email,
            "classroom_id": str(invitation.classroom_id),
        }

