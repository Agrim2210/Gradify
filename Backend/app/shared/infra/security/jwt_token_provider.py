from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, ExpiredSignatureError, jwt

from app.shared.application.security.token_payload import TokenPayload
from app.shared.application.security.token_provider import TokenProvider
from app.core.jwt_setting import JWTSettings
from app.shared.domain.enums.token_type import TokenType


class InvalidTokenException(Exception):
    pass


class ExpiredTokenException(Exception):
    pass


class JWTTokenProvider(TokenProvider):

    def __init__(
        self,
        settings: JWTSettings,
    ):
        self._settings = settings


    def issue_access_token(
        self,
        user_id: UUID,
    ) -> str:

        return self._create_token(
            user_id=user_id,
            expires_delta=timedelta(
                minutes=self._settings.access_token_expiry_minutes,
            ),
            token_type=TokenType.ACCESS,
        )

    def issue_refresh_token(
        self,
        user_id: UUID,
    ) -> str:

        return self._create_token(
            user_id=user_id,
            expires_delta=timedelta(
                days=self._settings.refresh_token_expiry_days,
            ),
            token_type=TokenType.REFRESH,
        )

    def verify_access_token(
        self,
        token: str,
    ) -> TokenPayload:

        return self._verify_token(
            token=token,
            expected_type=TokenType.ACCESS,
        )

    def verify_refresh_token(
        self,
        token: str,
    ) -> TokenPayload:

        return self._verify_token(
            token=token,
            expected_type=TokenType.REFRESH,
        )

    
    def _create_token(
        self,
        *,
        user_id: UUID,
        expires_delta: timedelta,
        token_type: TokenType,
    ) -> str:

        now = datetime.now(UTC)

        payload = {
            "sub": str(user_id),
            "type": token_type.value,
            "iat": int(now.timestamp()),
            "exp": int((now + expires_delta).timestamp()),
        }

        return jwt.encode(
            payload,
            self._settings.secret_key,
            algorithm=self._settings.algorithm,
        )

    def _verify_token(
        self,
        *,
        token: str,
        expected_type: TokenType,
    ) -> TokenPayload:

        try:

            payload = jwt.decode(
                token,
                self._settings.secret_key,
                algorithms=[self._settings.algorithm],
            )

        except ExpiredSignatureError:
            raise ExpiredTokenException()

        except JWTError:
            raise InvalidTokenException()

        if payload.get("type") != expected_type.value:
            raise InvalidTokenException()

        return TokenPayload(
            user_id=UUID(payload["sub"]),
            issued_at=datetime.fromtimestamp(
                payload["iat"],
                tz=UTC,
            ),
            expires_at=datetime.fromtimestamp(
                payload["exp"],
                tz=UTC,
            ),
        )