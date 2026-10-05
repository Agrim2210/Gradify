from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ResponseCreateWorkspace(BaseModel):
    id: UUID
    name: str
    slug: str

class WorkspaceItemSchema(BaseModel):
    id: UUID
    name: str
    slug: str
    role: str
    description: str | None = None
    created_at: datetime | None = None

class ResponseGetMe(BaseModel):
    workspace_name: str
    slug: str
    role: str
    workspaces: list[WorkspaceItemSchema] = []
    