from app.infra.database.base import Base
from sqlalchemy.orm import Mapped,mapped_column
from .models import PendingRegistrationModel
from sqlalchemy import ForeignKey,DateTime
from uuid import UUID
from datetime import datetime

class VerificationTokenModel(Base):
    __tablename__="verification_tokens"
    id:Mapped[UUID]=mapped_column(primary_key=True)
    registration_id:Mapped[UUID]=mapped_column(ForeignKey("pending_registration.id"))
    token_hash:Mapped[str]=mapped_column(nullable=False)
    expires_at:Mapped[datetime]=mapped_column(DateTime(timezone=True))
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True))
    used_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
