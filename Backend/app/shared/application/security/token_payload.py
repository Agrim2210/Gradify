from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
@dataclass(frozen=True, slots=True)
class TokenPayload:
    user_id: UUID
    issued_at: datetime
    expires_at: datetime