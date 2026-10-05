from app.modules.auth.application.enums.outbox_enum import EventType

EVENT_QUEUE_MAP={
    EventType.SEND_VERIFICATION_EMAIL:"verification_email_queue",
    EventType.PASSWORD_RESET:"verification_email_queue",
    EventType.SEND_WORKSPACE_INVITATION:"verification_email_queue",
    EventType.NOTE_UPLOADED:"verification_email_queue",
}
