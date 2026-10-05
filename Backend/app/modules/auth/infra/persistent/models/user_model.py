from app.infra.database.base import Base
from sqlalchemy.orm import Mapped,mapped_column
from uuid import UUID
from datetime import datetime
from sqlalchemy import String,DateTime,UUID

class UserModel(Base):
    __tablename__="user"
    id:Mapped[UUID]=mapped_column(UUID(as_uuid=True),primary_key=True)
    email:Mapped[str]=mapped_column(String,unique=True,nullable=False)
    password_hash:Mapped[str]=mapped_column(String,nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)
    verified_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)
    