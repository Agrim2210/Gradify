from abc import ABC,abstractmethod
from app.modules.workspace.domain.entities.workspace import Workspace
from uuid import UUID
class WorkspaceRepo(ABC):
    @abstractmethod
    async def save(self,workspace:Workspace)->None:
        ...
    @abstractmethod
    async def get_by_id(self,id:UUID):
        ...
    @abstractmethod
    async def get_by_ids(self, ids: list[UUID]) -> list[Workspace]:
        ...
    @abstractmethod
    async def get_by_slug(self,slug:str):
        ...
    @abstractmethod
    async def exist_by_slug(self,slug:str)->bool:
        ...
                
            