from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    Integer,
    JSON,
    String,
)
from app.modules.auth.application.dto.outbox_dto import Payload

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.database.base import Base
from app.modules.auth.application.enums.outbox_enum import EventType,Status
from sqlalchemy.types import TypeDecorator, JSON
from dataclasses import asdict

class EmailPayloadType(TypeDecorator):
    impl = JSON

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return asdict(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return Payload(**value)

class OutboxEventModel(Base):

    __tablename__ = "outbox_events"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType),
        nullable=False,
    )

    payload: Mapped[Payload] = mapped_column(EmailPayloadType()
        ,
        nullable=False,
    )

    status: Mapped[Status] = mapped_column(
        Enum(Status),
        nullable=False,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    next_retry: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_error_message: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )