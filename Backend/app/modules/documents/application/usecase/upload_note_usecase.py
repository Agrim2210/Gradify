from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.infra.database.uow import uow_contract
from app.modules.auth.application.dto.outbox_dto import Payload
from app.modules.auth.application.enums.outbox_enum import EventType
from app.modules.auth.application.outbox.outbox_event import OutBoxEvent
from app.modules.auth.application.outbox.outbox_repo import OutboxRepo
from app.modules.auth.infra.persistent.models.models import UserModel
from app.modules.documents.application.dto.note_dto import NoteResponseDTO, UploadNoteCommand
from app.modules.documents.domain.entities.note import Note
from app.modules.documents.domain.exception.exception import (
    ClassroomAccessDenied,
    ClassroomNotFound,
    InvalidFileTypeError,
)
from app.modules.documents.domain.repositories.note_repo import NoteRepo
from app.modules.documents.domain.repositories.storage_service import StorageService
from app.modules.workspace.domain.enums.classroom_role import ClassroomRole
from app.modules.workspace.infra.database.classroom_models import ClassroomMembershipModel, ClassroomModel


class UploadNoteUseCase:
    def __init__(
        self,
        session: AsyncSession,
        note_repo: NoteRepo,
        storage_service: StorageService,
        outbox_repo: OutboxRepo,
        uow: uow_contract,
    ):
        self._session = session
        self._note_repo = note_repo
        self._storage_service = storage_service
        self._outbox_repo = outbox_repo
        self._uow = uow

    async def execute(self, command: UploadNoteCommand) -> NoteResponseDTO:
        if not (command.file_name.lower().endswith(".pdf") or command.content_type == "application/pdf"):
            raise InvalidFileTypeError()

        classroom = await self._session.get(ClassroomModel, command.classroom_id)
        if classroom is None:
            raise ClassroomNotFound()

        # Check permissions: workspace OWNER, classroom creator, assigned teacher, or classroom OWNER
        from app.modules.workspace.infra.database.membership_sql import WorkspaceMembershipModel
        from app.modules.workspace.domain.enums.workspace_role import WorkspaceRole
        ws_mem = (
            await self._session.execute(
                select(WorkspaceMembershipModel).where(
                    WorkspaceMembershipModel.workspace_id == classroom.workspace_id,
                    WorkspaceMembershipModel.user_id == command.user_id,
                )
            )
        ).scalar_one_or_none()
        if ws_mem is None:
            raise ClassroomAccessDenied()

        allowed = False
        if ws_mem.role == WorkspaceRole.OWNER:
            allowed = True
        elif ws_mem.role == WorkspaceRole.TEACHER:
            if classroom.created_by_user_id == command.user_id or classroom.assigned_teacher_id == command.user_id:
                allowed = True
            else:
                membership = (
                    await self._session.execute(
                        select(ClassroomMembershipModel).where(
                            ClassroomMembershipModel.classroom_id == command.classroom_id,
                            ClassroomMembershipModel.user_id == command.user_id,
                            ClassroomMembershipModel.role == ClassroomRole.OWNER,
                        )
                    )
                ).scalar_one_or_none()
                if membership is not None:
                    allowed = True

        if not allowed:
            raise ClassroomAccessDenied()

        note_id = uuid4()
        clean_filename = command.file_name.replace(" ", "_")
        file_key = f"classrooms/{command.classroom_id}/notes/{note_id}/{clean_filename}"

        await self._storage_service.upload_file(
            file_obj=command.file_obj,
            file_key=file_key,
            content_type="application/pdf",
        )

        now = datetime.now(timezone.utc)
        note = Note(
            id=note_id,
            classroom_id=command.classroom_id,
            uploaded_by_user_id=command.user_id,
            title=command.title,
            description=command.description,
            file_name=command.file_name,
            file_key=file_key,
            file_size=command.file_size,
            mime_type="application/pdf",
            created_at=now,
        )
        await self._note_repo.save(note)

        student_stmt = (
            select(UserModel.email)
            .join(ClassroomMembershipModel, ClassroomMembershipModel.user_id == UserModel.id)
            .where(
                ClassroomMembershipModel.classroom_id == command.classroom_id,
                ClassroomMembershipModel.role == ClassroomRole.STUDENT,
            )
        )
        student_emails = (await self._session.execute(student_stmt)).scalars().all()

        note_url = f"{settings.FRONTEND_URL.rstrip('/')}/classrooms/{command.classroom_id}/notes"

        for student_email in student_emails:
            event = OutBoxEvent.create(
                payload=Payload(
                    email=student_email,
                    classroom_name=classroom.name,
                    note_title=note.title,
                    note_url=note_url,
                ),
                event_type=EventType.NOTE_UPLOADED,
            )
            self._outbox_repo.add(event)

        await self._uow.commit()

        view_url = self._storage_service.generate_presigned_view_url(note.file_key)
        download_url = self._storage_service.generate_presigned_download_url(note.file_key, note.file_name)

        return NoteResponseDTO(
            id=note.id,
            classroom_id=note.classroom_id,
            uploaded_by_user_id=note.uploaded_by_user_id,
            title=note.title,
            description=note.description,
            file_name=note.file_name,
            file_size=note.file_size,
            mime_type=note.mime_type,
            created_at=note.created_at,
            view_url=view_url,
            download_url=download_url,
        )
