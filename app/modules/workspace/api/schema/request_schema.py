from uuid import UUID
from pydantic import BaseModel, EmailStr
from app.modules.workspace.domain.enums.workspace_role import WorkspaceRole


class CreateWorkspaceRequest(BaseModel):
    name: str
    description: str | None = None


class InviteMemberRequest(BaseModel):
    email: EmailStr
    role: WorkspaceRole = WorkspaceRole.TEACHER


class AcceptInvitationRequest(BaseModel):
    password: str


class UpdateMemberRoleRequest(BaseModel):
    role: WorkspaceRole


class CreateClassroomRequest(BaseModel):
    name: str
    assigned_teacher_id: UUID | None = None


class InviteStudentRequest(BaseModel):
    email: EmailStr


class AcceptClassroomInvitationRequest(BaseModel):
    password: str
    roll_number: str


class BatchInviteStudentsRequest(BaseModel):
    emails: list[str]
