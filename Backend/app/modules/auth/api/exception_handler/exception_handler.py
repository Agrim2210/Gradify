from fastapi import Request
from fastapi.responses import JSONResponse
from app.modules.auth.domain.exception.user_exception import UserAlreadyExist
from app.modules.auth.application.use_cases.login_use_case import (
    InvalidCredentialsException,
    EmailNotVerifiedException,
)
from app.modules.auth.domain.exception.token_exception import TokenExpired, TokenUsed, InvalidToken

async def user_already_exist_handler(request: Request, exc: UserAlreadyExist):
    return JSONResponse(content={"error": str(exc), "detail": str(exc)}, status_code=409)

async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsException):
    return JSONResponse(content={"error": "Invalid email or password", "detail": "Invalid email or password"}, status_code=401)

async def email_not_verified_handler(request: Request, exc: EmailNotVerifiedException):
    return JSONResponse(
        content={
            "error": "Email not verified. Please check your email to activate your account.",
            "detail": "Email not verified. Please check your email to activate your account.",
            "email": exc.email,
            "code": "EMAIL_NOT_VERIFIED",
        },
        status_code=403,
    )

async def invalid_token_handler(request: Request, exc: Exception):
    return JSONResponse(content={"error": "Verification token is invalid or expired", "detail": "Verification token is invalid or expired"}, status_code=400)

async def invalid_reset_token_handler(request: Request, exc: Exception):
    return JSONResponse(content={"error": "Reset token is invalid or expired", "detail": "Reset token is invalid or expired"}, status_code=400)

def register_exception_handlers(app):
    app.add_exception_handler(UserAlreadyExist, user_already_exist_handler)
    app.add_exception_handler(InvalidCredentialsException, invalid_credentials_handler)
    app.add_exception_handler(EmailNotVerifiedException, email_not_verified_handler)
    app.add_exception_handler(TokenExpired, invalid_token_handler)
    app.add_exception_handler(TokenUsed, invalid_token_handler)
    app.add_exception_handler(InvalidToken, invalid_token_handler)
