from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String,DateTime,UUID,Enum
from app.infra.database.base import Base
from app.modules.workspace.domain.enums.workspace_status import WorkspaceStatus
from datetime import datetime
class WorkspaceModel(Base):
    __tablename__="workspace"
    id:Mapped[UUID]=mapped_column(UUID(as_uuid=True),primary_key=True)
    name:Mapped[str]=mapped_column(String(50),nullable=False)
    slug:Mapped[str]=mapped_column(String(50),unique=True,nullable=False)
    status:Mapped[WorkspaceStatus]=mapped_column(Enum(WorkspaceStatus,name="workspace_status"),nullable=False)
    description:Mapped[str|None]=mapped_column(String(100),nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=True)
    
    
    
    
    
    