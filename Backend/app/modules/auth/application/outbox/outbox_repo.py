from abc import ABC,abstractmethod
from app.modules.auth.application.outbox.outbox_event import OutBoxEvent
class OutboxRepo(ABC):
    @abstractmethod
    def add(self,event:OutBoxEvent):
        pass
    @abstractmethod
    async def get_pending(self,limit:int):
        pass
    @abstractmethod
    async def update(self,event:OutBoxEvent):
        pass
    @abstractmethod
    async def get_by_id(self,event_id):
        pass
    
















