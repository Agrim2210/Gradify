import secrets
import hashlib
from app.modules.auth.domain.interface.verification_token_repo import VerificationTokenGenerator,VerificationTokenHasher

class SecureVerificationToken(VerificationTokenGenerator):
   def __init__(self):
    self._length=32
   def generate_token(self)->str:
    return secrets.token_urlsafe(self._length) 


class SHA256VerificationTokenHasher(VerificationTokenHasher):
    def __init__(self):
        pass


    def hash_token(self,token: str) -> str:

        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

