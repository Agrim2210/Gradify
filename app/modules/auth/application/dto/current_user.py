from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
@dataclass(frozen=True)
class CurrentUser:
    id: UUID
    email: str
    created_at: datetime
    verified_at: datetime