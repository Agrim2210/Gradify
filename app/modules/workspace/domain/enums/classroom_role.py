from enum import Enum


class ClassroomRole(str, Enum):
    OWNER = "OWNER"
    STUDENT = "STUDENT"
