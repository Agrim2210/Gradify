from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse
from app.modules.auth.application.use_cases.pending_registration_usecase import PendingRegistrationUseCase
from app.modules.auth.application.dto.register_user import RegisterUser
from app.modules.auth.api.schemas.signup_schema import SignUpSchema
from app.modules.auth.infra.tasks.email_tasks import (
    deliver_verification_email_bg,
    deliver_direct_verification_email_bg,
)
from app.modules.auth.domain.entities.verification_token import VerificationToken
from app.modules.auth.bootstrap.dependencies import (
    get_use_case,
    get_email_use_case,
    get_login_use_case,
    get_request_password_reset_usecase,
    get_reset_password_usecase,
    get_pending_reg_repo,
    get_verification_token_repo,
    get_token_generator,
    get_token_hasher,
    get_uow,
    get_user_repo,
)
from app.modules.auth.application.use_cases.verify_email_usecase import EmailVerificationUseCase
from app.modules.auth.api.schemas.login_request import LoginRequest
from app.modules.auth.api.schemas.login_response import LoginResponse
from app.modules.auth.application.dto.login_command import LoginCommand
from app.modules.auth.application.use_cases.login_use_case import LoginUseCase
from app.modules.auth.application.use_cases.password_reset_usecase import RequestPasswordReset, ResetPassword
from app.modules.auth.api.schemas.password_reset import ForgotPasswordRequest, ResetPasswordRequest
from app.core.config import settings
from pydantic import BaseModel, EmailStr


class ResendVerificationRequest(BaseModel):
    email: EmailStr

route = APIRouter()

@route.post("/signup")
async def register_user(
    request: SignUpSchema,
    background_tasks: BackgroundTasks,
    use_case: PendingRegistrationUseCase = Depends(get_use_case),
):
    command = RegisterUser(
        email=request.email,
        password=request.password,
    )
    result = await use_case.execute(command)
    raw_token = result.get("raw_token")
    if raw_token:
        background_tasks.add_task(
            deliver_direct_verification_email_bg,
            request.email,
            raw_token,
            result.get("outbox_id"),
        )

    return JSONResponse(
        content={
            "message": "User registered successfully. Please check your email for the verification link.",
            "email": request.email,
            "raw_token": raw_token,
        },
        status_code=201,
    )

@route.post("/resend-verification")
async def resend_verification(
    request: ResendVerificationRequest,
    background_tasks: BackgroundTasks,
    pending_repo = Depends(get_pending_reg_repo),
    user_repo = Depends(get_user_repo),
    token_repo = Depends(get_verification_token_repo),
    token_gen = Depends(get_token_generator),
    token_hasher = Depends(get_token_hasher),
    uow = Depends(get_uow),
):
    existing_user = await user_repo.get_by_email(request.email)
    if existing_user:
        return JSONResponse(
            content={"message": "This email is already verified. Please sign in.", "status": "already_verified"},
            status_code=200,
        )

    pending = await pending_repo.get_by_email(request.email)
    if not pending:
        return JSONResponse(
            content={"error": "No pending registration found for this email. Please sign up first."},
            status_code=404,
        )

    raw_token = token_gen.generate_token()
    token_hash = token_hasher.hash_token(raw_token)
    await token_repo.delete_by_registration_id(pending.id)
    verification_token = VerificationToken.create(
        registration_id=pending.id,
        token_hash=token_hash,
    )
    token_repo.add(verification_token)
    await uow.commit()

    background_tasks.add_task(
        deliver_direct_verification_email_bg,
        request.email,
        raw_token,
    )

    return JSONResponse(
        content={
            "message": f"Fresh verification email dispatched to {request.email}.",
            "email": request.email,
            "raw_token": raw_token,
        },
        status_code=200,
    )



@route.get("/verify-email")
async def verify_email(
    token: str,
    redirect: bool = False,
    use_case: EmailVerificationUseCase = Depends(get_email_use_case),
):
    result = await use_case.execute(token)
    if redirect:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/?token={token}&status=verified",
            status_code=307,
        )
    return JSONResponse(
        content={
            "message": "email verified successfully",
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "email": result["user"].email,
            "user_id": str(result["user"].id),
        },
        status_code=200,
    )

@route.post("/Login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    use_case: LoginUseCase = Depends(get_login_use_case),
):
    command = LoginCommand(
        email=request.email,
        password=request.password,
    )
    result = await use_case.execute(command)
    return LoginResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )

@route.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    use_case: RequestPasswordReset = Depends(get_request_password_reset_usecase),
):
    await use_case.execute(request.email)
    return {"message": "If the email exists, a password reset link has been sent"}

@route.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    use_case: ResetPassword = Depends(get_reset_password_usecase),
):
    await use_case.execute(request.token, request.new_password)
    return {"message": "Password updated successfully"}
