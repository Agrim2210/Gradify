from app.modules.auth.application.dto.login_command import LoginCommand
from app.modules.auth.application.dto.login_result import LoginResult
from app.modules.auth.domain.interface.user_repo import UserRepo
from app.modules.auth.domain.interface.password_hashing_repo import PasswordHasher
from app.shared.application.security.token_provider import TokenProvider
from app.infra.database.uow import uow_contract


from app.modules.auth.domain.interface.pending_registration_repo import PendingRegistrationRepository

class InvalidCredentialsException(Exception):
    pass

class EmailNotVerifiedException(Exception):
    def __init__(self, email: str = ""):
        self.email = email
        super().__init__(f"Email {email} is not verified. Please check your email to activate your account.")

class LoginUseCase:

    def __init__(
        self,
        user_repo: UserRepo,
        password_hasher: PasswordHasher,
        token_provider: TokenProvider,
        uow: uow_contract,
        pending_repo: PendingRegistrationRepository | None = None,
    ):
        self.user_repo = user_repo
        self.password_hasher = password_hasher
        self.token_provider = token_provider
        self.uow = uow
        self.pending_repo = pending_repo

    async def execute(
        self,
        command: LoginCommand,
    ) -> LoginResult:

        user = await self.user_repo.get_by_email(
            command.email,
        )
        print(user)
        if user is None:
            if self.pending_repo is not None:
                pending = await self.pending_repo.get_by_email(command.email)
                if pending is not None:
                    raise EmailNotVerifiedException(email=command.email)
            raise InvalidCredentialsException()

        password_valid = self.password_hasher.verify_hash(
            password=command.password,
            password_hash=user.password_hash,
        )
        print(password_valid)
        if not password_valid:
            raise InvalidCredentialsException()

        access_token = self.token_provider.issue_access_token(
            user.id,
        )

        refresh_token = self.token_provider.issue_refresh_token(
            user.id,
        )

        return LoginResult(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        