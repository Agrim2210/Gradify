from app.modules.workspace.domain.repositories.workspace_repo import WorkspaceRepo
from app.modules.workspace.domain.entities.workspace import Workspace
from app.modules.workspace.infra.database.models import WorkspaceModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
class WorkspaceSQLREPO(WorkspaceRepo):
    def __init__(self,Session:AsyncSession):
        self.session=Session
    async def save(self,workspace:Workspace)->None:
        model=WorkspaceModel(
            id=workspace.id,
            name=workspace.name,
            slug=workspace.slug,
            status=workspace.status,
            description=workspace.description,
            created_at=workspace.created_at,
            updated_at=workspace.updated_at
        )
        self.session.add(model)
    async def get_by_id(self, id:UUID):
        workspace=await self.session.get(WorkspaceModel,id)
        if not workspace:
            return None
        return Workspace(
            id=workspace.id,
            name=workspace.name,
            slug=workspace.slug,
            status=workspace.status,
            description=workspace.description,
            created_at=workspace.created_at,
            updated_at=workspace.updated_at
        )

    async def get_by_ids(self, ids: list[UUID]) -> list[Workspace]:
        if not ids:
            return []
        stmt = select(WorkspaceModel).where(WorkspaceModel.id.in_(ids))
        execute = await self.session.execute(stmt)
        models = execute.scalars().all()
        return [
            Workspace(
                id=m.id,
                name=m.name,
                slug=m.slug,
                status=m.status,
                description=m.description,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in models
        ]

    async def get_by_slug(self,slug:str):
        stmt=select(WorkspaceModel).where(WorkspaceModel.slug==slug)
        execute = await self.session.execute(stmt)
        workspace=execute.scalar_one_or_none()
        if not workspace:
            return None
        return Workspace(
            id=workspace.id,
            name=workspace.name,
            slug=workspace.slug,
            status=workspace.status,
            description=workspace.description,
            created_at=workspace.created_at,
            updated_at=workspace.updated_at
        )
    async def exist_by_slug(self, slug):  
        stmt=select(WorkspaceModel).where(WorkspaceModel.slug==slug)
        execute= await self.session.execute(stmt)
        res=execute.scalar_one_or_none()
        if not res:
            return False
        return True
    
        
            
        
            
            
            
        