from enum import Enum


class WorkspaceRole(str, Enum):
    OWNER = "OWNER"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"