from dataclasses import dataclass
from datetime import datetime
from typing import BinaryIO
from uuid import UUID


@dataclass
class UploadNoteCommand:
    classroom_id: UUID
    user_id: UUID
    title: str
    description: str | None
    file_name: str
    content_type: str
    file_size: int
    file_obj: BinaryIO


@dataclass
class NoteResponseDTO:
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
    student_emails: list[str] | None = None
    classroom_name: str | None = None
