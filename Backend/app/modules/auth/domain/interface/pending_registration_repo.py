from abc import ABC,abstractmethod
from uuid import UUID
from app.modules.auth.domain.entities.pending_registration_entity import PendingRegistration
class PendingRegistrationRepository(ABC):
    @abstractmethod
    async def add(self,registration:PendingRegistration):
        pass
    @abstractmethod
    async def get_by_email(self,email:str):
        pass
    @abstractmethod
    async def get_by_uuid(self, uuid: UUID) -> PendingRegistration | None:
        pass
    @abstractmethod
    async def delete(self, uuid: UUID) -> None:
        pass

    @abstractmethod
    async def update(self, registration: PendingRegistration) -> None:
        pass

   
