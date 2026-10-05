from datetime import datetime,UTC,timedelta
from uuid import UUID,uuid4
from dataclasses import dataclass
from app.modules.workspace.domain.enums.workspace_status import WorkspaceStatus


@dataclass
class Workspace:
    id:UUID
    name:str
    slug:str
    description:str|None
    status:WorkspaceStatus
    created_at:datetime
    updated_at:datetime|None
    @classmethod
    def create(cls,name:str,slug:str,description:str|None,updated_at:datetime|None):
        id=uuid4()
        created_at=datetime.now(UTC)
        return cls(id=id,name=name,slug=slug,description=description,status=WorkspaceStatus.ACTIVE,created_at=created_at,updated_at=updated_at)
    def rename(self,new_name:str)->None:
        if not new_name.strip():
            raise ValueError(" Workspace Name Cannot be Empty")
        self.name=new_name.strip()
    def archive(self)->None:
        self.status=WorkspaceStatus.ARCHIVED
    def change_description(self,new_description:str|None)->None: 
        self.description=new_description       