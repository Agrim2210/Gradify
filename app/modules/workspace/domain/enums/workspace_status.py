from enum import Enum
class WorkspaceStatus(str,Enum):
    ACTIVE="ACTIVE"
    ARCHIVED="ARCHIVED"
    DELETED="DELETED"
    