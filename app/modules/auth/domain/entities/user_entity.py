from datetime import datetime,UTC
from uuid import UUID,uuid4
class User:
    def __init__(self,id:UUID,email:str,password_hash:str,created_at:datetime,verified_at:datetime):
        self.id=id
        self.email=email
        self.password_hash=password_hash
        self.created_at=created_at
        self.verified_at=verified_at
    @classmethod
    def create(cls,email:str,password_hash:str,created_at:datetime):
        id=uuid4()
        now=datetime.now(UTC)
        return cls(id=id,email=email,password_hash=password_hash,created_at=created_at,verified_at=now)    

    def change_password(self, password_hash: str) -> None:
        self.password_hash = password_hash
        
