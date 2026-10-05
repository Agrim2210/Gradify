from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.documents.domain.entities.note import Note
from app.modules.documents.domain.repositories.note_repo import NoteRepo
from app.modules.documents.infra.database.note_model import ClassroomNoteModel


class NoteSQLRepo(NoteRepo):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, note: Note) -> None:
        model = ClassroomNoteModel(
            id=note.id,
            classroom_id=note.classroom_id,
            uploaded_by_user_id=note.uploaded_by_user_id,
            title=note.title,
            description=note.description,
            file_name=note.file_name,
            file_key=note.file_key,
            file_size=note.file_size,
            mime_type=note.mime_type,
            created_at=note.created_at,
        )
        self._session.add(model)

    async def get_by_id(self, note_id: UUID) -> Note | None:
        model = await self._session.get(ClassroomNoteModel, note_id)
        if model is None:
            return None
        return self._to_entity(model)

    async def list_by_classroom_id(self, classroom_id: UUID) -> list[Note]:
        stmt = (
            select(ClassroomNoteModel)
            .where(ClassroomNoteModel.classroom_id == classroom_id)
            .order_by(ClassroomNoteModel.created_at.desc())
        )
        result = await self._session.scalars(stmt)
        models = result.all()
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: ClassroomNoteModel) -> Note:
        return Note(
            id=model.id,
            classroom_id=model.classroom_id,
            uploaded_by_user_id=model.uploaded_by_user_id,
            title=model.title,
            description=model.description,
            file_name=model.file_name,
            file_key=model.file_key,
            file_size=model.file_size,
            mime_type=model.mime_type,
            created_at=model.created_at,
        )
