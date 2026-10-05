"""Auth outbox-to-Celery dispatcher, invoked by Celery Beat."""
import asyncio

from app.core.config import settings
from app.infra.database.session import SessionLocal
from app.modules.auth.application.enums.event_queue_map import EVENT_QUEUE_MAP
from app.modules.auth.infra.persistent.repositories.sqlalchemy_outbox_repository import SQLAlchemyOutboxRepository
from app.shared.infra.celery.app import celery_app


async def _dispatch_pending_events() -> int:
    async with SessionLocal() as session:
        repository = SQLAlchemyOutboxRepository(session)
        events = await repository.get_pending(settings.CELERY_OUTBOX_BATCH_SIZE)
        dispatched = 0
        try:
            for event in events:
                queue = EVENT_QUEUE_MAP.get(event.event_type)
                if queue is None:
                    event.mark_failed(f"No Celery queue configured for {event.event_type}")
                    await repository.update(event)
                    continue

                # Broker publication and the DB commit are separate resources. A
                # crash between them intentionally leaves a PENDING record, giving
                # at-least-once rather than potentially losing the event.
                celery_app.send_task(
                    "auth.email.send_verification_email",
                    args=[str(event.id)],
                    queue=queue,
                )
                event.mark_publish()
                await repository.update(event)
                dispatched += 1
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        return dispatched


@celery_app.task(name="auth.outbox.dispatch_pending", ignore_result=True)
def dispatch_pending() -> int:
    return asyncio.run(_dispatch_pending_events())
