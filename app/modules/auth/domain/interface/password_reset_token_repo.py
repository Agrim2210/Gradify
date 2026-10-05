from abc import ABC, abstractmethod

from app.modules.auth.domain.entities.password_reset_token import PasswordResetToken


class PasswordResetTokenRepo(ABC):
    @abstractmethod
    def add(self, token: PasswordResetToken) -> None:
        ...

    @abstractmethod
    async def get_by_hash(self, token_hash: str) -> PasswordResetToken | None:
        ...

    @abstractmethod
    async def update(self, token: PasswordResetToken) -> None:
        ...
