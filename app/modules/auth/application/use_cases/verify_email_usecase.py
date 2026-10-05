from app.modules.auth.domain.interface.verification_token_repo import VerificationTokenHasher
from app.modules.auth.domain.interface.pending_registration_repo import PendingRegistrationRepository
from app.modules.auth.domain.entities.user_entity import User
from app.modules.auth.domain.interface.user_repo import UserRepo
from app.modules.auth.domain.interface.verification_token_query_repo import VerificationTokenQueryRepo
from app.shared.application.security.token_provider import TokenProvider
from app.infra.database.uow import uow_contract
from app.modules.auth.domain.exception.user_exception import UserAlreadyExist

from app.modules.auth.domain.exception.token_exception import InvalidToken

class EmailVerificationUseCase:
    def __init__(
        self,
        user_repo: UserRepo,
        registration_repo: PendingRegistrationRepository,
        uow: uow_contract,
        token_repo: VerificationTokenQueryRepo,
        token_hasher: VerificationTokenHasher,
        token_provider: TokenProvider,
    ):
        self.user_repo = user_repo
        self.registration_repo = registration_repo
        self.uow = uow
        self.token_repo = token_repo
        self.token_hasher = token_hasher
        self.token_provider = token_provider

    async def execute(self, token: str):
        token_hash = self.token_hasher.hash_token(token)
        registration = await self.token_repo.get_by_hash(token_hash)
        if not registration:
            raise InvalidToken("Invalid or expired verification token")
        registration.ensure_usable()
        pending_registration = await self.registration_repo.get_by_uuid(registration.registration_id)
        if not pending_registration:
            raise InvalidToken("Pending registration record not found")

        existing_user = await self.user_repo.get_by_email(pending_registration.email)
        if existing_user:
            # User already verified — issue tokens and allow seamless entry
            access_token = self.token_provider.issue_access_token(existing_user.id)
            refresh_token = self.token_provider.issue_refresh_token(existing_user.id)
            return {
                "user": existing_user,
                "access_token": access_token,
                "refresh_token": refresh_token,
            }


        # Convert pending registration to permanent active user
        user = User.create(
            email=pending_registration.email,
            password_hash=pending_registration.password_hash,
            created_at=pending_registration.created_at,
        )

        try:
            self.user_repo.add(user)
            await self.token_repo.delete_by_registration_id(pending_registration.id)
            await self.uow.flush()
            await self.registration_repo.delete(pending_registration.id)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

        # Generate JWT access and refresh tokens so user is immediately logged in
        access_token = self.token_provider.issue_access_token(user.id)
        refresh_token = self.token_provider.issue_refresh_token(user.id)

        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
