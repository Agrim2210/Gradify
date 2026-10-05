from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class LoginCommand:
    email: str
    password: str