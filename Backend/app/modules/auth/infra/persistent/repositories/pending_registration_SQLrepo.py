from app.modules.auth.domain.entities.pending_registration_entity import PendingRegistration
from sqlalchemy import select 
from app.modules.auth.infra.persistent.models.models import PendingRegistrationModel
from app.modules.auth.domain.interface.pending_registration_repo import PendingRegistrationRepository
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
class SQLPendingRegistrationRepo(PendingRegistrationRepository):
    def __init__(self,session:AsyncSession):
        self.session=session
    def add(self,registration:PendingRegistration):
        model=PendingRegistrationModel(

            id=registration.id,
            email=registration.email,
            password_hash=registration.password_hash,
            created_at=registration.created_at
        )
        self.session.add(model)
    async def get_by_email(self,email:str):
        stmt=select(PendingRegistrationModel).where(PendingRegistrationModel.email==email)
        user = await self.session.execute(stmt)
        res=user.scalar_one_or_none()
        if not res:
            return None
        return PendingRegistration(
            id=res.id,
            email=res.email,
            password_hash=res.password_hash,
            created_at=res.created_at

        )    
    async def delete(self,uuid:UUID)->None:
        stmt=select(PendingRegistrationModel).where(PendingRegistrationModel.id==uuid)
        user = await self.session.execute(stmt)
        res=user.scalar_one_or_none()
        if not res:
            return None
        await self.session.delete(res)
    async def get_by_uuid(self,uuid:UUID)->PendingRegistration:
        stmt=select(PendingRegistrationModel).where(PendingRegistrationModel.id==uuid)
        user = await self.session.execute(stmt)
        res=user.scalar_one_or_none()
        if not res:
            return None
        return PendingRegistration(
            id=res.id,
            email=res.email,
            password_hash=res.password_hash,
            created_at=res.created_at,
        )

    async def update(self, registration: PendingRegistration) -> None:
        model = await self.session.get(PendingRegistrationModel, registration.id)
        if model:
            model.password_hash = registration.password_hash



