from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "gradify",
    broker=settings.REDIS_URL,
    include=[
        "app.modules.auth.infra.tasks.outbox_tasks",
        "app.modules.auth.infra.tasks.email_tasks",
    ],
)
celery_app.conf.update(
    task_default_queue="default",
    task_routes={
        "auth.email.send_verification_email": {"queue": "verification_email_queue"},
    },
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_ignore_result=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    beat_schedule={
        "dispatch-auth-outbox": {
            "task": "auth.outbox.dispatch_pending",
            "schedule": settings.CELERY_OUTBOX_POLL_SECONDS,
        }
    },
)

from app.modules.auth.infra.tasks import email_tasks, outbox_tasks  
