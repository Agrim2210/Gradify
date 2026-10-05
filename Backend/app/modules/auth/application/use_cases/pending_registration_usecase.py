from app.modules.auth.domain.interface.password_hashing_repo import PasswordHasher
from app.modules.auth.domain.interface.pending_registration_repo import PendingRegistrationRepository
from app.modules.auth.domain.interface.user_repo import UserRepo
from app.modules.auth.domain.entities.pending_registration_entity import PendingRegistration
from app.modules.auth.application.dto.register_user import RegisterUser
from app.modules.auth.domain.exception.user_exception import UserAlreadyExist
from app.modules.auth.domain.entities.verification_token import VerificationToken
from app.modules.auth.domain.interface.verification_token_query_repo import VerificationTokenQueryRepo as token_repo
from app.modules.auth.application.outbox.outbox_event import OutBoxEvent
from app.modules.auth.application.outbox.outbox_repo import OutboxRepo
from app.modules.auth.domain.interface.verification_token_repo import VerificationTokenGenerator as token_generator,VerificationTokenHasher as token_hasher
from app.infra.database.uow import uow_contract
from app.modules.auth.application.enums.outbox_enum import EventType
from app.modules.auth.application.dto.outbox_dto import Payload

class PendingRegistrationUseCase:
    def __init__(
        self,
        user_repo: PendingRegistrationRepository,
        token_repo: token_repo,
        token_generator: token_generator,
        token_hasher: token_hasher,
        password_hasher: PasswordHasher,
        uow: uow_contract,
        outbox_repo: OutboxRepo,
        actual_user_repo: UserRepo | None = None,
    ):
        self.user_repo = user_repo
        self.password_hasher = password_hasher
        self.token_repo = token_repo
        self.token_generator = token_generator
        self.token_hasher = token_hasher
        self.uow = uow
        self.outbox_repo = outbox_repo
        self.actual_user_repo = actual_user_repo

    async def execute(self, command: RegisterUser) -> dict:
        if self.actual_user_repo:
            active_user = await self.actual_user_repo.get_by_email(command.email)
            if active_user:
                raise UserAlreadyExist(f"User with email {command.email} already exists. Please sign in.")

        password_hash = self.password_hasher.create_hash(command.password)
        raw_token = self.token_generator.generate_token()
        token_hash = self.token_hasher.hash_token(token=raw_token)

        exist = await self.user_repo.get_by_email(command.email)
        if exist:
            registration_id = exist.id
            await self.token_repo.delete_by_registration_id(registration_id)
        else:
            registration = PendingRegistration.create(email=command.email, password_hash=password_hash)
            registration_id = registration.id
            self.user_repo.add(registration)

        verification_token = VerificationToken.create(
            registration_id=registration_id,
            token_hash=token_hash,
        )
        outbox = OutBoxEvent.create(
            payload=Payload(email=command.email, raw_token=raw_token),
            event_type=EventType.SEND_VERIFICATION_EMAIL,
        )

        try:
            self.token_repo.add(verification_token)
            self.outbox_repo.add(outbox)
            await self.uow.commit()
        except Exception as e:
            print(f"[PendingRegistrationUseCase Error] {e}")
            await self.uow.rollback()
            raise e

        return {
            "email": command.email,
            "raw_token": raw_token,
            "outbox_id": str(outbox.id),
        }