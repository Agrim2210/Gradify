import re

from pydantic import BaseModel, EmailStr, field_validator


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8 or not re.search(r"[A-Z]", value) or not re.search(r"\d", value) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password does not meet complexity requirements")
        return value
