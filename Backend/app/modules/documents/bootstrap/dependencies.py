from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.database.session import get_db
from app.infra.database.uow import uow_contract, uow_implementation
from app.modules.auth.application.outbox.outbox_repo import OutboxRepo
from app.modules.auth.infra.persistent.repositories.sqlalchemy_outbox_repository import SQLAlchemyOutboxRepository
from app.modules.documents.application.usecase.assignment_service import AssignmentService
from app.modules.documents.application.usecase.get_note_usecase import GetNoteUseCase
from app.modules.documents.application.usecase.list_notes_usecase import ListNotesUseCase
from app.modules.documents.application.usecase.upload_note_usecase import UploadNoteUseCase
from app.modules.documents.domain.repositories.note_repo import NoteRepo
from app.modules.documents.domain.repositories.storage_service import StorageService
from app.modules.documents.infra.database.repositories.note_sql_repo import NoteSQLRepo
from app.modules.documents.infra.storage.backblaze_storage_service import BackblazeB2StorageService


def get_storage_service() -> StorageService:
    return BackblazeB2StorageService()


def get_note_repo(session: AsyncSession = Depends(get_db)) -> NoteRepo:
    return NoteSQLRepo(session)


def get_outbox_repo(session: AsyncSession = Depends(get_db)) -> OutboxRepo:
    return SQLAlchemyOutboxRepository(session)


def get_uow(session: AsyncSession = Depends(get_db)) -> uow_contract:
    return uow_implementation(session)


def get_upload_note_usecase(
    session: AsyncSession = Depends(get_db),
    note_repo: NoteRepo = Depends(get_note_repo),
    storage_service: StorageService = Depends(get_storage_service),
    outbox_repo: OutboxRepo = Depends(get_outbox_repo),
    uow: uow_contract = Depends(get_uow),
) -> UploadNoteUseCase:
    return UploadNoteUseCase(
        session=session,
        note_repo=note_repo,
        storage_service=storage_service,
        outbox_repo=outbox_repo,
        uow=uow,
    )


def get_list_notes_usecase(
    session: AsyncSession = Depends(get_db),
    note_repo: NoteRepo = Depends(get_note_repo),
    storage_service: StorageService = Depends(get_storage_service),
) -> ListNotesUseCase:
    return ListNotesUseCase(
        session=session,
        note_repo=note_repo,
        storage_service=storage_service,
    )


def get_note_usecase(
    session: AsyncSession = Depends(get_db),
    note_repo: NoteRepo = Depends(get_note_repo),
    storage_service: StorageService = Depends(get_storage_service),
) -> GetNoteUseCase:
    return GetNoteUseCase(
        session=session,
        note_repo=note_repo,
        storage_service=storage_service,
    )


def get_assignment_service(
    session: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(get_storage_service),
    uow: uow_contract = Depends(get_uow),
) -> AssignmentService:
    return AssignmentService(session=session, storage=storage, uow=uow)
