from app.core.config import settings
from app.infra.database.uow import uow_contract
from app.modules.auth.application.dto.outbox_dto import Payload
from app.modules.auth.application.enums.outbox_enum import EventType
from app.modules.auth.application.outbox.outbox_event import OutBoxEvent
from app.modules.auth.application.outbox.outbox_repo import OutboxRepo
from app.modules.auth.domain.entities.password_reset_token import PasswordResetToken
from app.modules.auth.domain.interface.password_hashing_repo import PasswordHasher
from app.modules.auth.domain.interface.password_reset_token_repo import PasswordResetTokenRepo
from app.modules.auth.domain.interface.user_repo import UserRepo
from app.modules.auth.domain.interface.verification_token_repo import VerificationTokenGenerator, VerificationTokenHasher


class RequestPasswordReset:
    def __init__(self, user_repo: UserRepo, token_repo: PasswordResetTokenRepo, token_generator: VerificationTokenGenerator, token_hasher: VerificationTokenHasher, outbox_repo: OutboxRepo, uow: uow_contract):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.token_generator = token_generator
        self.token_hasher = token_hasher
        self.outbox_repo = outbox_repo
        self.uow = uow

    async def execute(self, email: str) -> dict | None:
        user = await self.user_repo.get_by_email(email)
        if user is None:
            return None
        raw_token = self.token_generator.generate_token()
        token = PasswordResetToken.create(user.id, self.token_hasher.hash_token(raw_token))
        reset_url = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={raw_token}"
        event = OutBoxEvent.create(Payload(email=user.email, reset_url=reset_url), EventType.PASSWORD_RESET)
        try:
            self.token_repo.add(token)
            self.outbox_repo.add(event)
            await self.uow.commit()
            return {
                "email": user.email,
                "reset_url": reset_url,
                "outbox_id": str(event.id),
                "raw_token": raw_token,
            }
        except Exception:
            await self.uow.rollback()
            raise


class ResetPassword:
    def __init__(self, user_repo: UserRepo, token_repo: PasswordResetTokenRepo, token_hasher: VerificationTokenHasher, password_hasher: PasswordHasher, uow: uow_contract):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.token_hasher = token_hasher
        self.password_hasher = password_hasher
        self.uow = uow

    async def execute(self, raw_token: str, new_password: str) -> None:
        token = await self.token_repo.get_by_hash(self.token_hasher.hash_token(raw_token))
        if token is None:
            from app.modules.auth.domain.exception.token_exception import TokenExpired
            raise TokenExpired()
        token.ensure_usable()
        user = await self.user_repo.get_by_id(token.user_id)
        if user is None:
            from app.modules.auth.domain.exception.token_exception import TokenExpired
            raise TokenExpired()
        user.change_password(self.password_hasher.create_hash(new_password))
        token.mark_used()
        try:
            await self.user_repo.update(user)
            await self.token_repo.update(token)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise
