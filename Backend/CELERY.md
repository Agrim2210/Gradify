# Celery + transactional outbox

The API transaction writes the registration data and `outbox_events` row together.  It never sends an email directly.

Celery Beat runs the Auth module's `auth.outbox.dispatch_pending` task every `CELERY_OUTBOX_POLL_SECONDS` seconds. It reads committed `PENDING` rows, publishes a small task containing the outbox UUID to Redis, then records the row as `PUBLISHED`. The Auth Celery worker consumes `verification_email_queue`, loads that row, sends SMTP mail, and records it as `COMPLETED`.

The shared Celery transport configuration lives in `app/shared/infra/celery/`; Auth-specific outbox and email task adapters live in `app/modules/auth/infra/tasks/`. There are no custom Redis-list consumers, publishers, or application-managed worker loops.

Start Redis, then run these in separate terminals from the project root:

```powershell
myenv\Scripts\celery -A app.shared.infra.celery.app.celery_app worker -l INFO -Q verification_email_queue,default
myenv\Scripts\celery -A app.shared.infra.celery.app.celery_app beat -l INFO
```

Add these values to `.env` (do not commit SMTP credentials):

```dotenv
REDIS_URL=redis://localhost:6379/0
CELERY_OUTBOX_POLL_SECONDS=5
CELERY_OUTBOX_BATCH_SIZE=100
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-account@example.com
SMTP_PASSWORD=your-app-password
SMTP_SENDER_EMAIL=your-account@example.com
```

Apply the included migration before starting the workers:

```powershell
myenv\Scripts\alembic upgrade head
```

Delivery is **at least once**, not exactly once. A crash after Redis accepts a task but before Postgres is updated can enqueue it again; a crash after SMTP accepts mail but before Celery acknowledges it can also retry. This is the correct trade-off for not losing mail. For strict duplicate suppression, use an email provider idempotency key or record a provider message ID before retrying.
