from fastapi import Depends
from app.modules.auth.infra.persistent.repositories.verification_token_Repo import VerificationTokenSQL
from app.modules.auth.infra.security.verification_token import SHA256VerificationTokenHasher,SecureVerificationToken
from app.modules.auth.domain.interface.verification_token_query_repo import VerificationTokenQueryRepo
from app.modules.auth.domain.interface.verification_token_repo import VerificationTokenGenerator,VerificationTokenHasher
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.database.session import get_db
from app.infra.database.uow import uow_implementation,uow_contract
from app.modules.auth.infra.persistent.repositories.pending_registration_SQLrepo import SQLPendingRegistrationRepo
from app.modules.auth.infra.security.argon2_password_hasher import Argon2PasswordHasher
from app.modules.auth.domain.interface.password_hashing_repo import PasswordHasher
from app.modules.auth.domain.interface.pending_registration_repo import PendingRegistrationRepository
from app.modules.auth.application.use_cases.pending_registration_usecase import PendingRegistrationUseCase
from app.modules.auth.application.outbox.outbox_repo import OutboxRepo
from app.modules.auth.infra.persistent.repositories.sqlalchemy_outbox_repository import SQLAlchemyOutboxRepository
from app.modules.auth.application.use_cases.pending_registration_usecase import PendingRegistrationUseCase
from app.modules.auth.application.use_cases.verify_email_usecase import EmailVerificationUseCase
from app.modules.auth.domain.interface.user_repo import UserRepo
from app.modules.auth.infra.persistent.repositories.user_SQLREPO import UserSQLRepo
from app.modules.auth.application.use_cases.login_use_case import LoginUseCase
from app.shared.application.security.token_provider import TokenProvider
from app.shared.infra.security.jwt_token_provider import JWTTokenProvider  
from app.core.jwt_setting import JWTSettings 
from app.modules.auth.application.dto.current_user import CurrentUser
from app.modules.auth.domain.interface.password_reset_token_repo import PasswordResetTokenRepo
from app.modules.auth.infra.persistent.repositories.password_reset_token_repo import PasswordResetTokenSQLRepo
from app.modules.auth.application.use_cases.password_reset_usecase import RequestPasswordReset, ResetPassword
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

def get_pending_reg_repo(db:AsyncSession=Depends(get_db))->PendingRegistrationRepository:
    return SQLPendingRegistrationRepo(db)
def get_password_hasher()->PasswordHasher:
    return Argon2PasswordHasher()
def get_verification_token_repo(db:AsyncSession=Depends(get_db))-> VerificationTokenQueryRepo:
    return VerificationTokenSQL(db)
def get_token_generator()->VerificationTokenGenerator:
    return SecureVerificationToken()
def get_token_hasher()->VerificationTokenHasher:

    return SHA256VerificationTokenHasher ()       
def get_outbox_repo(db:AsyncSession=Depends(get_db))->OutboxRepo:
    return SQLAlchemyOutboxRepository(db)
def get_uow(db:AsyncSession=Depends(get_db))->uow_contract:
    return uow_implementation(db)
def get_user_repo(db:AsyncSession=Depends(get_db))->UserRepo:
    return UserSQLRepo(db)
def get_password_reset_token_repo(db:AsyncSession=Depends(get_db))->PasswordResetTokenRepo:
    return PasswordResetTokenSQLRepo(db)
def get_use_case(
    user_repo: PendingRegistrationRepository = Depends(get_pending_reg_repo),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_repo: VerificationTokenQueryRepo = Depends(get_verification_token_repo),
    token_generator: VerificationTokenGenerator = Depends(get_token_generator),
    token_hash: VerificationTokenHasher = Depends(get_token_hasher),
    uow: uow_contract = Depends(get_uow),
    outbox_repo: OutboxRepo = Depends(get_outbox_repo),
    actual_user_repo: UserRepo = Depends(get_user_repo),
) -> PendingRegistrationUseCase:
    return PendingRegistrationUseCase(
        user_repo=user_repo,
        password_hasher=password_hasher,
        token_repo=token_repo,
        token_generator=token_generator,
        token_hasher=token_hash,
        uow=uow,
        outbox_repo=outbox_repo,
        actual_user_repo=actual_user_repo,
    )
def get_token_provider()->TokenProvider:
    return JWTTokenProvider(JWTSettings())
def get_email_use_case(user_repo:UserRepo=Depends(get_user_repo),registration_repo:PendingRegistrationRepository=Depends(get_pending_reg_repo),uow:uow_contract=Depends(get_uow),token_repo:VerificationTokenQueryRepo=Depends(get_verification_token_repo),token_hasher:VerificationTokenHasher=Depends(get_token_hasher),token_provider:TokenProvider=Depends(get_token_provider))->EmailVerificationUseCase:
    return EmailVerificationUseCase(user_repo=user_repo,registration_repo=registration_repo,uow=uow,token_repo=token_repo,token_hasher=token_hasher,token_provider=token_provider)
def get_login_use_case(
    user_repo: UserRepo = Depends(get_user_repo),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_provider: TokenProvider = Depends(get_token_provider),
    uow: uow_contract = Depends(get_uow),
    pending_repo: PendingRegistrationRepository = Depends(get_pending_reg_repo),
) -> LoginUseCase:
    return LoginUseCase(
        user_repo=user_repo,
        password_hasher=password_hasher,
        token_provider=token_provider,
        uow=uow,
        pending_repo=pending_repo,
    )
def get_request_password_reset_usecase(user_repo:UserRepo=Depends(get_user_repo),token_repo:PasswordResetTokenRepo=Depends(get_password_reset_token_repo),token_generator:VerificationTokenGenerator=Depends(get_token_generator),token_hasher:VerificationTokenHasher=Depends(get_token_hasher),outbox_repo:OutboxRepo=Depends(get_outbox_repo),uow:uow_contract=Depends(get_uow))->RequestPasswordReset:
    return RequestPasswordReset(user_repo, token_repo, token_generator, token_hasher, outbox_repo, uow)
def get_reset_password_usecase(user_repo:UserRepo=Depends(get_user_repo),token_repo:PasswordResetTokenRepo=Depends(get_password_reset_token_repo),token_hasher:VerificationTokenHasher=Depends(get_token_hasher),password_hasher:PasswordHasher=Depends(get_password_hasher),uow:uow_contract=Depends(get_uow))->ResetPassword:
    return ResetPassword(user_repo, token_repo, token_hasher, password_hasher, uow)
async def get_current_user(authorization: HTTPAuthorizationCredentials = Depends(security),token_provider:TokenProvider=Depends(get_token_provider),user_repo:UserRepo=Depends(get_user_repo)):
    token = authorization.credentials
    payload=token_provider.verify_access_token(token)
    user=await user_repo.get_by_id(payload.user_id)
    if not user:
        raise Exception("User not found")
    return CurrentUser(id=user.id,email=user.email,created_at=user.created_at,verified_at=user.verified_at)
