from dataclasses import dataclass
@dataclass(frozen=True)
class Payload:
    email:str
    raw_token:str|None=None
    invitation_url:str|None=None
    workspace_name:str|None=None
    reset_url:str|None=None
    classroom_name:str|None=None
    classroom_invitation_url:str|None=None
    note_title:str|None=None
    note_url:str|None=None
    role:str|None=None
