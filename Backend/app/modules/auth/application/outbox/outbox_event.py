from uuid import UUID,uuid4
from datetime import datetime,timedelta
from ...application.enums.outbox_enum import EventType,Status
class OutBoxEvent:
    def __init__(self,id:UUID,event_type:EventType,payload:dict,status:Status,created_at:datetime,retry_count:int|0,next_retry:datetime|None,last_error_message:str|None,published_at:datetime|None):
        self.id=id
        self.event_type=event_type
        self.payload=payload
        self.created_at=created_at
        self.status=status
        self.retry_count=retry_count
        self.next_retry=next_retry
        self.last_error_message=last_error_message
        self.published_at=published_at
    @classmethod
    def create(cls,payload:dict,event_type:EventType):
        return cls(id=uuid4(),event_type=event_type,payload=payload,status=Status.PENDING
        ,created_at=datetime.now(),retry_count=0,next_retry=None,last_error_message=None,published_at=None)    
    def mark_publish(self):
        self.status=Status.PUBLISHED
        self.published_at=datetime.now()
        self.last_error_message=None
    def mark_completed(self):
        self.status=Status.COMPLETED
        self.last_error_message=None
    def mark_failed(self,error:str):
        self.status=Status.FAILED
        self.retry_count+=1
        self.last_error_message=error
    def schedule_retry(self,after:timedelta):
        self.status=Status.PENDING
        self.next_retry=datetime.now()+after
    def can_retry(self,now:datetime):
        if self.status!=Status.PENDING:
            return False
        if self.next_retry is None:
            return True
        return now>=self.next_retry                

