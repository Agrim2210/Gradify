from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.application.outbox.outbox_event import OutBoxEvent
from app.modules.auth.application.outbox.outbox_repo import OutboxRepo
from app.modules.auth.infra.persistent.models.outbox_model import OutboxEventModel
from datetime import datetime, UTC
from sqlalchemy import and_, or_
from app.modules.auth.application.enums.outbox_enum import Status,EventType
from app.modules.auth.infra.persistent.models.outbox_model import EmailPayloadType
class SQLAlchemyOutboxRepository(
    OutboxRepo,
):

    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session
    def add(
    self,
    event: OutBoxEvent,
) -> None:

        model = OutboxEventModel(
    
            id=event.id,
    
            event_type=event.event_type,
    
            payload=event.payload,
    
            status=event.status,
    
            retry_count=event.retry_count,
    
            created_at=event.created_at,
    
            published_at=event.published_at,
    
            next_retry=event.next_retry,
    
            last_error_message=event.last_error_message
            )
    
        self._session.add(model)    
    async def update(
    self,
    event: OutBoxEvent,
) -> None:

        model = await self._session.get(
            OutboxEventModel,
            event.id,
        )
    
        if model is None:
            return
    
        model.status = event.status
        model.retry_count = event.retry_count
        model.published_at = event.published_at
        model.next_retry = event.next_retry
        model.last_error_message = event.last_error_message    
        
    
    async def get_pending(    
    self,
    limit: int,
    ) -> list[OutBoxEvent]:
    
        now = datetime.now(UTC)
    
        stmt = (
            select(OutboxEventModel)
            .where(
                and_(
                    OutboxEventModel.status == Status.PENDING,
                    or_(
                        OutboxEventModel.next_retry.is_(None),
                        OutboxEventModel.next_retry <= now,
                    ),
                )
            )
            .order_by(OutboxEventModel.created_at)
            .limit(limit)
            # Several Celery Beat instances can run safely: each one skips rows
            # currently being dispatched by another instance.
            .with_for_update(skip_locked=True)
        )
    
        result = await self._session.scalars(stmt)
    
        models = result.all()
    
        return [
            self._to_entity(model)
            for model in models
        ]

    async def get_by_id(self, event_id) -> OutBoxEvent | None:
        model = await self._session.get(OutboxEventModel, event_id)
        return self._to_entity(model) if model is not None else None



    def _to_entity(
        self,
        model: OutboxEventModel,
    ) -> OutboxEvent:
    
        return OutBoxEvent(
    
            id=model.id,
    
            event_type=model.event_type,
    
            payload=model.payload,
    
            status=model.status,
    
            retry_count=model.retry_count,
    
            created_at=model.created_at,
    
            published_at=model.published_at,
    
            next_retry=model.next_retry,
    
            last_error_message=model.last_error_message,
        )
