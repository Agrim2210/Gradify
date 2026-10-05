from dataclasses import dataclass
@dataclass(frozen=True)
class RegisterUser:
    email:str
    password:str
    