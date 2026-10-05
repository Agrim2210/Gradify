from abc import ABC,abstractmethod
from app.modules.auth.domain.entities.verification_token import VerificationToken
class VerificationTokenQueryRepo(ABC):
    @abstractmethod
    async def add(self,token:VerificationToken)->None:
        pass
    @abstractmethod
    async def get_by_hash(self,hash:str)->VerificationToken|None :
        pass
    @abstractmethod
    async def update(self,token:VerificationToken)->None:
        pass

    @abstractmethod
    async def delete(self,token:VerificationToken)->None:
        pass

    @abstractmethod
    async def delete_by_registration_id(self, registration_id) -> None:
        pass

