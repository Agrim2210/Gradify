from abc import ABC,abstractmethod

class PasswordHasher(ABC):
    @abstractmethod
    def create_hash(self,password:str)->str:
        pass
    @abstractmethod
    def verify_hash(self,password:str,password_hash:str)-> bool:
        pass
    @abstractmethod
    def needs_rehash(self,password_hash:str)-> bool:
        pass
    