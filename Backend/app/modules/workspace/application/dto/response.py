from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class ResponseCreateWorkspace:
    id: UUID
    name: str
    slug: str