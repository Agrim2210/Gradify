from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class NoteResponse(BaseModel):
    id: UUID
    classroom_id: UUID
    uploaded_by_user_id: UUID
    title: str
    description: str | None
    file_name: str
    file_size: int
    mime_type: str
    created_at: datetime
    view_url: str | None = None
    download_url: str | None = None

    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    notes: list[NoteResponse]
