from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.documents.application.dto.note_dto import NoteResponseDTO
from app.modules.documents.domain.exception.exception import ClassroomAccessDenied, ClassroomNotFound
from app.modules.documents.domain.repositories.note_repo import NoteRepo
from app.modules.documents.domain.repositories.storage_service import StorageService
from app.modules.workspace.domain.enums.classroom_role import ClassroomRole
from app.modules.workspace.infra.database.classroom_models import ClassroomMembershipModel, ClassroomModel


class ListNotesUseCase:
    def __init__(
        self,
        session: AsyncSession,
        note_repo: NoteRepo,
        storage_service: StorageService,
    ):
        self._session = session
        self._note_repo = note_repo
        self._storage_service = storage_service

    async def execute(self, classroom_id: UUID, user_id: UUID) -> list[NoteResponseDTO]:
        classroom = await self._session.get(ClassroomModel, classroom_id)
        if classroom is None:
            raise ClassroomNotFound()

        from app.modules.workspace.infra.database.membership_sql import WorkspaceMembershipModel
        from app.modules.workspace.domain.enums.workspace_role import WorkspaceRole
        ws_membership = (
            await self._session.execute(
                select(WorkspaceMembershipModel).where(
                    WorkspaceMembershipModel.workspace_id == classroom.workspace_id,
                    WorkspaceMembershipModel.user_id == user_id,
                )
            )
        ).scalar_one_or_none()
        if ws_membership is None:
            raise ClassroomAccessDenied()

        if ws_membership.role == WorkspaceRole.TEACHER:
            if classroom.created_by_user_id != user_id and classroom.assigned_teacher_id != user_id:
                mem = (
                    await self._session.execute(
                        select(ClassroomMembershipModel.id).where(
                            ClassroomMembershipModel.classroom_id == classroom_id,
                            ClassroomMembershipModel.user_id == user_id,
                            ClassroomMembershipModel.role == ClassroomRole.OWNER,
                        )
                    )
                ).scalar_one_or_none()
                if mem is None:
                    raise ClassroomAccessDenied()

        notes = await self._note_repo.list_by_classroom_id(classroom_id)
        result = []
        for note in notes:
            view_url = self._storage_service.generate_presigned_view_url(note.file_key)
            download_url = self._storage_service.generate_presigned_download_url(note.file_key, note.file_name)
            result.append(
                NoteResponseDTO(
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
            )
        return result
