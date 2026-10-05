from celery import uuid

from app.modules.auth.domain.interface.user_repo import UserRepo
from app.modules.auth.domain.entities.user_entity import User
from app.modules.auth.infra.persistent.models.models import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID  
from sqlalchemy import select
class UserSQLRepo(UserRepo):
    def __init__(self,session:AsyncSession):
        self.session=session
    def add(self,user:User)->None:
        user_model=UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            created_at=user.created_at,
            verified_at=user.verified_at
        )
        self.session.add(user_model)
    async def get_by_email(self,email:str)->User|None:
        stmt=select(UserModel).where(UserModel.email==email)
        user = await self.session.execute(stmt)
        res=user.scalar_one_or_none()
        if not res:
            return None
        return User(
            id=res.id,
            email=res.email,
            password_hash=res.password_hash,
            created_at=res.created_at,
            verified_at=res.verified_at
        )
    async def get_by_id(self,id:UUID)->User|None:
        user=await self.session.get(UserModel,id)
        if not user:
            return None
        return User(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            created_at=user.created_at,
            verified_at=user.verified_at
        )
    async def update(self,user:User)->None:
        model=await self.session.get(UserModel,user.id)
        if model:
            model.password_hash=user.password_hash
        
    
