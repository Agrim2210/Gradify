from datetime import datetime,UTC,timedelta
from uuid import UUID,uuid4
from app.modules.auth.domain.exception.token_exception import TokenExpired,TokenUsed

class VerificationToken:
    def __init__(self,id:UUID,registration_id:UUID,token_hash:str,expires_at:datetime,created_at:datetime,used_at:datetime|None=None):
        self.id=id
        self.registration_id =registration_id
        self.token_hash = token_hash
        self.expires_at = expires_at
        self.created_at = created_at
        self.used_at = used_at
    @classmethod
    def create(cls,registration_id:UUID,token_hash:str,expiration_hours:int=24):
        now=datetime.now(UTC)
        return cls(id=uuid4(),registration_id=registration_id,token_hash=token_hash,expires_at=(now+timedelta(hours=expiration_hours)),created_at=now,used_at=None)

    
    def is_expired(self)->bool:
        return (datetime.now(UTC)>=self.expires_at )
    def is_used(self)->bool:
        return self.used_at is not None
    def mark_used(self):
        self.used_at=datetime.now(UTC)

    def ensure_usable(self):
        if self.is_expired():
            raise TokenExpired()
        if self.is_used():
            raise TokenUsed()
