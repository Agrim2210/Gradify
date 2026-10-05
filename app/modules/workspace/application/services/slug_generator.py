from slugify import slugify
from app.modules.workspace.domain.repositories.workspace_repo import WorkspaceRepo
class SlugGenerator:
    def __init__(self,workspace_repo:WorkspaceRepo):
        self.workspace_repo=workspace_repo
    async def generate(self, workspace_name: str) -> str:
        base_slug = slugify(workspace_name)
        slug = base_slug
        counter = 2
        while await self.workspace_repo.exist_by_slug(slug):
            slug = f"{base_slug}--{counter}"
            counter += 1
        return slug    
            
            