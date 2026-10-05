from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.auth.domain.entities.verification_token import VerificationToken
from app.modules.auth.infra.persistent.models.verification_token_model import VerificationTokenModel
from app.modules.auth.domain.interface.verification_token_query_repo import VerificationTokenQueryRepo
class VerificationTokenSQL(VerificationTokenQueryRepo):
    def __init__(self,session:AsyncSession):
        self.session=session
    def add(self,token:VerificationToken)->None:
        data=VerificationTokenModel(
            id=token.id,
            registration_id=token.registration_id,
            token_hash=token.token_hash,
            expires_at=token.expires_at,
            created_at=token.created_at,
            used_at=token.used_at
            )
        self.session.add(data)
    async def get_by_hash(self,token_hash:str)->VerificationToken|None :
        stmt=select(VerificationTokenModel).where(VerificationTokenModel.token_hash==token_hash)
        token=await self.session.execute(stmt)
        res=token.scalar_one_or_none()
        if not res:
            return None
        return VerificationToken(
            id=res.id,
            registration_id=res.registration_id,
            token_hash=res.token_hash,
            expires_at=res.expires_at,
            created_at=res.created_at,
            used_at=res.used_at
        )   
    async def update(self,token:VerificationToken) ->None:
        res=await self.session.get(VerificationTokenModel,token.id)
        if not res:
            return 
        res.used_at=token.used_at
        res.expires_at=token.expires_at
    async def delete(self,token:VerificationToken)->None:
        res=await self.session.get(VerificationTokenModel,token.id)
        if res:
            await self.session.delete(res)

    async def delete_by_registration_id(self, registration_id: UUID) -> None:
        from sqlalchemy import delete
        stmt = delete(VerificationTokenModel).where(VerificationTokenModel.registration_id == registration_id)
        await self.session.execute(stmt)

