from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class LoginResult:
    access_token: str
    refresh_token: str