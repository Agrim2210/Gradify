from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.infra.database.session import get_db
from app.core.config import settings
from app.modules.auth.api.routes.auth_route import route as auth_route
from app.modules.auth.api.exception_handler.exception_handler import register_exception_handlers
from app.modules.workspace.api.routes.workspace_route import router as workspace_router
from app.modules.workspace.api.exception_handler.exception_handler import (
    register_workspace_exception_handlers,
)
from app.modules.documents.api.routes.document_route import router as document_router
from app.modules.documents.api.exception_handler.exception_handler import (
    register_document_exception_handlers,
)

app = FastAPI(title=settings.APP_NAME)

@app.get("/health")
async def check_health():
    return {
        "status":"healthy",
        "environment":settings.APP_ENV
    }
@app.get("/db_health")
async def db_health(db:AsyncSession=Depends(get_db)):
    res=await db.execute(text("Select 1"))
    return {"database":res.scalar()}    
app.include_router(auth_route,tags=["create_identity"])    
app.include_router(workspace_router,tags=["workspace"])    
app.include_router(document_router,tags=["documents"])
register_exception_handlers(app)
register_workspace_exception_handlers(app)
register_document_exception_handlers(app)
