"""Auth outbox dispatcher, supporting both direct in-process SMTP and Celery."""
import asyncio

from app.core.config import settings
from app.infra.database.session import SessionLocal
from app.modules.auth.application.enums.event_queue_map import EVENT_QUEUE_MAP
from app.modules.auth.infra.persistent.repositories.sqlalchemy_outbox_repository import SQLAlchemyOutboxRepository
from app.shared.infra.celery.app import celery_app
from app.shared.infra.email.smtp_email_sender import SMTPEmailSender


async def _dispatch_pending_events() -> int:
    """Dispatches pending events to Celery queue (for Celery Beat / Worker deployments)."""
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


async def _dispatch_pending_events_direct() -> int:
    """Dispatches pending outbox events directly via SMTPEmailSender without Celery."""
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        return 0

    sender = SMTPEmailSender(
        host=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USERNAME,
        password=settings.SMTP_PASSWORD,
        sender_email=settings.SMTP_SENDER_EMAIL or settings.SMTP_USERNAME,
    )

    async with SessionLocal() as session:
        repository = SQLAlchemyOutboxRepository(session)
        events = await repository.get_pending(settings.CELERY_OUTBOX_BATCH_SIZE)
        dispatched = 0
        for event in events:
            try:
                await sender.send_email(event.payload)
                event.mark_completed()
                await repository.update(event)
                dispatched += 1
            except Exception as exc:
                print(f"[DIRECT OUTBOX ERROR] Failed to dispatch event {event.id}: {exc}")
                event.mark_failed(str(exc))
                await repository.update(event)
        if dispatched > 0:
            await session.commit()
        return dispatched


async def run_inprocess_outbox_loop():
    """Background polling loop for FastAPI lifespan to process outbox directly."""
    while True:
        try:
            await asyncio.sleep(settings.CELERY_OUTBOX_POLL_SECONDS)
            if settings.ENABLE_INPROCESS_OUTBOX_POLLER:
                await _dispatch_pending_events_direct()
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[OUTBOX POLLER ERROR] {e}")
