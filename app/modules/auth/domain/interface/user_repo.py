from abc import ABC,abstractmethod
from app.modules.auth.domain.entities.user_entity import User
from uuid import UUID
class UserRepo(ABC):
    @abstractmethod
    def add(self,user:User)->None:
        pass
    @abstractmethod
    async def get_by_email(self,email:str)->User|None :
        pass
    @abstractmethod
    async def get_by_id(self,id:UUID)->User|None:
        pass 
    @abstractmethod
    async def update(self,user:User)->None:
        pass
  
