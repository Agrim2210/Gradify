from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from app.modules.auth.domain.exception.token_exception import TokenExpired, TokenUsed


class PasswordResetToken:
    def __init__(self, id: UUID, user_id: UUID, token_hash: str, expires_at: datetime, created_at: datetime, used_at: datetime | None = None):
        self.id = id
        self.user_id = user_id
        self.token_hash = token_hash
        self.expires_at = expires_at
        self.created_at = created_at
        self.used_at = used_at

    @classmethod
    def create(cls, user_id: UUID, token_hash: str) -> "PasswordResetToken":
        now = datetime.now(timezone.utc)
        return cls(uuid4(), user_id, token_hash, now + timedelta(hours=1), now)

    def ensure_usable(self) -> None:
        if self.used_at is not None:
            raise TokenUsed()
        if datetime.now(timezone.utc) >= self.expires_at:
            raise TokenExpired()

    def mark_used(self) -> None:
        self.used_at = datetime.now(timezone.utc)
