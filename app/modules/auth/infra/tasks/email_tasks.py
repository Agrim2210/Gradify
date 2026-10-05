"""Celery delivery adapter for auth verification-email events."""
import asyncio
from uuid import UUID

from app.core.config import settings
from app.infra.database.session import SessionLocal
from app.modules.auth.infra.persistent.repositories.sqlalchemy_outbox_repository import SQLAlchemyOutboxRepository
from app.shared.infra.celery.app import celery_app
from app.shared.infra.email.smtp_email_sender import SMTPEmailSender


async def _deliver_verification_email(event_id: str) -> None:
    async with SessionLocal() as session:
        repository = SQLAlchemyOutboxRepository(session)
        event = await repository.get_by_id(UUID(event_id))
        if event is None or event.status.value == "COMPLETED":
            return
        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            raise RuntimeError("SMTP_USERNAME and SMTP_PASSWORD must be configured")

        sender = SMTPEmailSender(
            host=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            sender_email=settings.SMTP_SENDER_EMAIL or settings.SMTP_USERNAME,
        )
        await sender.send_email(event.payload)
        event.mark_completed()
        await repository.update(event)
        await session.commit()


from app.modules.auth.application.dto.outbox_dto import Payload
import traceback

async def deliver_direct_verification_email_bg(email: str, raw_token: str, event_id: str | None = None) -> None:
    """Dispatches verification email directly via FastAPI BackgroundTasks with zero-dependency execution."""
    try:
        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            print("[AUTH ERROR] SMTP_USERNAME and SMTP_PASSWORD are not configured in settings")
            return

        sender = SMTPEmailSender(
            host=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            sender_email=settings.SMTP_SENDER_EMAIL or settings.SMTP_USERNAME,
        )
        payload = Payload(email=email, raw_token=raw_token)
        await sender.send_email(payload)
        print(f"[AUTH] Successfully dispatched verification email to {email}")

        if event_id:
            try:
                async with SessionLocal() as session:
                    repository = SQLAlchemyOutboxRepository(session)
                    event = await repository.get_by_id(UUID(event_id))
                    if event and event.status.value != "COMPLETED":
                        event.mark_completed()
                        await repository.update(event)
                        await session.commit()
            except Exception as db_err:
                print(f"[AUTH NOTE] Outbox record update note: {db_err}")
    except Exception as e:
        print(f"[AUTH ERROR] Failed to send verification email to {email}: {e}")
        traceback.print_exc()

async def deliver_verification_email_bg(event_id: str) -> None:
    """Dispatches verification email directly via FastAPI BackgroundTasks with error handling."""
    try:
        await _deliver_verification_email(event_id)
        print(f"[AUTH] Successfully sent verification email for event {event_id}")
    except Exception as e:
        print(f"[AUTH ERROR] Failed to send verification email for event {event_id}: {e}")
        traceback.print_exc()


async def deliver_workspace_invitation_email_bg(email: str, workspace_name: str, role: str, invitation_url: str) -> None:
    """Dispatches workspace invitation email directly via FastAPI BackgroundTasks."""
    try:
        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            print("[INVITE ERROR] SMTP credentials not configured in settings")
            return

        sender = SMTPEmailSender(
            host=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            sender_email=settings.SMTP_SENDER_EMAIL or settings.SMTP_USERNAME,
        )
        payload = Payload(
            email=email,
            invitation_url=invitation_url,
            workspace_name=workspace_name,
            role=role,
        )
        await sender.send_email(payload)
        print(f"[INVITE SUCCESS] Invitation email dispatched to {email} for workspace {workspace_name}")
    except Exception as e:
        print(f"[INVITE ERROR] Failed to send invitation email to {email}: {e}")
        traceback.print_exc()


async def deliver_classroom_invitation_email_bg(email: str, classroom_name: str, invitation_url: str) -> None:
    """Dispatches classroom student invitation email directly via FastAPI BackgroundTasks."""
    try:
        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            print("[CLASSROOM INVITE ERROR] SMTP credentials not configured in settings")
            return

        sender = SMTPEmailSender(
            host=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            sender_email=settings.SMTP_SENDER_EMAIL or settings.SMTP_USERNAME,
        )
        payload = Payload(
            email=email,
            classroom_invitation_url=invitation_url,
            classroom_name=classroom_name,
        )
        await sender.send_email(payload)
        print(f"[CLASSROOM INVITE SUCCESS] Invitation email dispatched to {email} for classroom {classroom_name}")
    except Exception as e:
        print(f"[CLASSROOM INVITE ERROR] Failed to send classroom invitation email to {email}: {e}")
        traceback.print_exc()



@celery_app.task(
    name="auth.email.send_verification_email",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
    acks_late=True,
    ignore_result=True,
)
def send_verification_email(self, event_id: str) -> None:
    asyncio.run(_deliver_verification_email(event_id))



