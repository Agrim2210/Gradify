
from abc import ABC, abstractmethod
from uuid import UUID
from app.shared.application.security.token_payload import TokenPayload
class TokenProvider(ABC):

    @abstractmethod
    def issue_access_token(
        self,
        user_id: UUID,
    ) -> str:
        ...

    @abstractmethod
    def issue_refresh_token(
        self,
        user_id: UUID,
    ) -> str:
        ...
    @abstractmethod
    def verify_access_token(
        self,
        token: str,
    ) -> "TokenPayload":
        ...    
    @abstractmethod
    def verify_refresh_token(
        self,
        token: str,
    ) -> "TokenPayload":
        ...
        