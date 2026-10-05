from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Note:
    id: UUID
    classroom_id: UUID
    uploaded_by_user_id: UUID
    title: str
    description: str | None
    file_name: str
    file_key: str
    file_size: int
    mime_type: str
    created_at: datetime
