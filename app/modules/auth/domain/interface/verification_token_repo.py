from abc import ABC,abstractmethod
class VerificationTokenGenerator(ABC):
    @abstractmethod
    def generate_token(self)->str:
        pass

class VerificationTokenHasher(ABC):
    @abstractmethod
    def hash_token(self,token:str)->str:
        pass    