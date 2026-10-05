from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.domain.entities.password_reset_token import PasswordResetToken
from app.modules.auth.domain.interface.password_reset_token_repo import PasswordResetTokenRepo
from app.modules.auth.infra.persistent.models.password_reset_token_model import PasswordResetTokenModel


class PasswordResetTokenSQLRepo(PasswordResetTokenRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, token: PasswordResetToken) -> None:
        self.session.add(PasswordResetTokenModel(**token.__dict__))

    async def get_by_hash(self, token_hash: str) -> PasswordResetToken | None:
        result = await self.session.execute(select(PasswordResetTokenModel).where(PasswordResetTokenModel.token_hash == token_hash))
        model = result.scalar_one_or_none()
        return PasswordResetToken(**{column.name: getattr(model, column.name) for column in model.__table__.columns}) if model else None

    async def update(self, token: PasswordResetToken) -> None:
        model = await self.session.get(PasswordResetTokenModel, token.id)
        if model:
            model.used_at = token.used_at
