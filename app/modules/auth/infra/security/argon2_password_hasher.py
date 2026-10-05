from app.modules.auth.domain.interface.password_hashing_repo import PasswordHasher
from argon2 import PasswordHasher as Argon2
from argon2.exceptions import VerifyMismatchError
class Argon2PasswordHasher(PasswordHasher):
    def __init__(self):
        self.time_cost=3
        self.memory_cost=65636
        self.parallelism=4
        self._hasher=Argon2(time_cost=self.time_cost,memory_cost=self.memory_cost,parallelism=self.parallelism)
    def create_hash(self,password:str)->str:
        return self._hasher.hash(password)    
    def verify_hash(self,password:str,password_hash:str)->bool:
        try :
            self._hasher.verify(password_hash,password)
            return True
        except VerifyMismatchError:
            return False
    def needs_rehash(self,password_hash:str)-> bool:
        return self._hasher.check_needs_rehash(password_hash)        

