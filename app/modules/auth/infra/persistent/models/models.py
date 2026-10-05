from sqlalchemy.orm import mapped_column,Mapped
from sqlalchemy import String,Boolean
from app.shared.database.mixins import UUIDMixin,TimestampMixin
from datetime import datetime
from uuid import UUID
from app.infra.database.base import Base
from sqlalchemy import DateTime

class UserModel(Base,UUIDMixin,TimestampMixin):
    __tablename__="users"
    email:Mapped[str]=mapped_column(String(250),unique=True,nullable=False)
    password_hash:Mapped[str]=mapped_column(String(250),nullable=False)
    is_active:Mapped[bool]=mapped_column(Boolean,default=True,nullable=False)
    verified_at:Mapped[datetime]=mapped_column(DateTime(timezone=True), nullable=False)



class PendingRegistrationModel(Base):
    __tablename__="pending_registration"
    id:Mapped[UUID]=mapped_column(primary_key=True)
    email:Mapped[str]=mapped_column(unique=True)
    password_hash:Mapped[str]=mapped_column(nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True))
            
