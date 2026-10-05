from abc import ABC,abstractmethod
from app.modules.auth.application.dto.outbox_dto import Payload
class EmailSender(ABC):
    @abstractmethod
    async def send_email(self,message:Payload)->None:
        pass