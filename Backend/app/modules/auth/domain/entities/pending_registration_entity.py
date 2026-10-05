from datetime import datetime,UTC
from uuid import UUID,uuid4
class PendingRegistration:
    def __init__(self,id:UUID,email:str,password_hash:str,created_at:datetime):
        self.id=id
        self.email=email
        self.password_hash=password_hash
        
        self.created_at=created_at
    @classmethod
    def create(cls,email:str,password_hash:str):
        return cls(id=uuid4(),email=email,password_hash=password_hash,created_at=datetime.now(UTC))    
