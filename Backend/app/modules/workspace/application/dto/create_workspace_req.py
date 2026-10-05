from dataclasses import dataclass
from uuid import UUID
@dataclass(frozen=True)
class RequestCreateWorkspace:
    name:str
    description:str|None
    user_id:UUID