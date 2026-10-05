from abc import ABC, abstractmethod
from uuid import UUID
from app.modules.documents.domain.entities.note import Note


class NoteRepo(ABC):
    @abstractmethod
    async def save(self, note: Note) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, note_id: UUID) -> Note | None:
        pass

    @abstractmethod
    async def list_by_classroom_id(self, classroom_id: UUID) -> list[Note]:
        pass
