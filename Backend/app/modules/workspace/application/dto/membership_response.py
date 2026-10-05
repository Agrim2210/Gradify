from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime

@dataclass
class WorkspaceItemDTO:
    id: UUID
    name: str
    slug: str
    role: str
    description: str | None = None
    created_at: datetime | None = None

@dataclass
class ResponseMembership:
    workspace_name: str
    slug: str
    role: str
    workspaces: list[WorkspaceItemDTO] = field(default_factory=list)

    