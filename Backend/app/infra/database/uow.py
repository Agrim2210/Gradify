from abc import ABC,abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
class uow_contract(ABC):
    @abstractmethod
    async def flush(self):
        pass
    @abstractmethod
    async def commit(self):
        pass
    @abstractmethod
    async def rollback(self):
        pass
class uow_implementation(uow_contract):
    def __init__(self,session:AsyncSession):
        self.session=session
    async def flush(self):
        await self.session.flush()
    async def commit(self):
        await self.session.commit()
    async def rollback(self):
        await self.session.rollback()
                    
