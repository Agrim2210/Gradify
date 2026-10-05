from uuid import UUID
from fastapi import APIRouter, BackgroundTasks, Depends

from app.modules.auth.bootstrap.dependencies import get_current_user
from app.modules.auth.infra.tasks.email_tasks import deliver_workspace_invitation_email_bg, deliver_classroom_invitation_email_bg
from app.modules.workspace.api.routes.workspace_context import get_workspace_context
from app.modules.workspace.api.schema.request_schema import (
    AcceptClassroomInvitationRequest,
    AcceptInvitationRequest,
    BatchInviteStudentsRequest,
    CreateClassroomRequest,
    CreateWorkspaceRequest,
    InviteMemberRequest,
    InviteStudentRequest,
    UpdateMemberRoleRequest,
)
from app.modules.workspace.domain.enums.workspace_role import WorkspaceRole
from app.modules.workspace.api.schema.response_schema import ResponseCreateWorkspace, ResponseGetMe, WorkspaceItemSchema
from app.modules.workspace.application.dto.create_workspace_req import RequestCreateWorkspace
from app.modules.workspace.application.dto.invite_member import InviteMemberCommand
from app.modules.workspace.application.usecase.accept_invitation import AcceptInvitation
from app.modules.workspace.application.usecase.change_member_role import ChangeMemberRole
from app.modules.workspace.application.usecase.classroom import ClassroomService
from app.modules.workspace.application.usecase.get_membership import GetMembershipUseCase
from app.modules.workspace.application.usecase.invite_member import InviteMember
from app.modules.workspace.bootstrap.dependencies import (
    get_accept_invitation_usecase,
    get_change_member_role_usecase,
    get_classroom_service,
    get_create_workspace_usecase,
    get_invite_member_usecase,
    get_membership_repo,
    get_membership_usecase,
    get_workspace_repo,
)
from app.modules.workspace.domain.exception.exception import WorkspaceAccessDenied, WorkspaceNotFound
from app.modules.workspace.domain.repositories.membership_repo import WorkspaceMembershipRepo
from app.modules.workspace.domain.repositories.workspace_repo import WorkspaceRepo

router = APIRouter(tags=["Workspace"])


@router.post("/create_workspace", response_model=ResponseCreateWorkspace)
async def create_workspace(
    request: CreateWorkspaceRequest,
    current_user=Depends(get_current_user),
    create_workspace_usecase=Depends(get_create_workspace_usecase),
):
    request_dto = RequestCreateWorkspace(name=request.name, description=request.description, user_id=current_user.id)
    usecase_response = await create_workspace_usecase.execute(request_dto)
    return ResponseCreateWorkspace(id=usecase_response.id, name=usecase_response.name, slug=usecase_response.slug)


@router.get("/Me", response_model=ResponseGetMe)
async def get_my_workspaces(
    slug: str | None = None,
    current_user=Depends(get_current_user),
    membership_usecase: GetMembershipUseCase = Depends(get_membership_usecase),
):
    use_case_response = await membership_usecase.execute(current_user.id, selected_slug=slug)
    if not use_case_response:
        raise WorkspaceNotFound()
    return ResponseGetMe(
        workspace_name=use_case_response.workspace_name,
        slug=use_case_response.slug,
        role=use_case_response.role,
        workspaces=[
            WorkspaceItemSchema(
                id=w.id,
                name=w.name,
                slug=w.slug,
                role=w.role,
                description=w.description,
                created_at=w.created_at,
            )
            for w in use_case_response.workspaces
        ],
    )



@router.get("/workspace_context/{slug}", response_model=ResponseGetMe)
async def get_workspace(workspace_context=Depends(get_workspace_context)):
    return ResponseGetMe(
        workspace_name=workspace_context.workspace_name,
        slug=workspace_context.workspace_slug,
        role=workspace_context.role,
    )


@router.post("/workspaces/{slug}/invitations", status_code=201)
async def invite_member(
    slug: str,
    request: InviteMemberRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    usecase: InviteMember = Depends(get_invite_member_usecase),
):
    invite_data = await usecase.execute(slug, current_user.id, InviteMemberCommand(email=request.email, role=request.role))
    # Directly dispatch styled invitation email via background tasks
    background_tasks.add_task(
        deliver_workspace_invitation_email_bg,
        email=invite_data["email"],
        workspace_name=invite_data["workspace_name"],
        role=invite_data["role"],
        invitation_url=invite_data["invitation_url"],
    )
    return {"message": "Invitation sent successfully", "invitation_url": invite_data["invitation_url"]}


@router.post("/workspaces/{slug}/students/batch-invite", status_code=201)
async def batch_invite_students(
    slug: str,
    request: BatchInviteStudentsRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    usecase: InviteMember = Depends(get_invite_member_usecase),
):
    invited = []
    skipped = []
    for raw_email in request.emails:
        email = raw_email.strip().lower()
        if not email or "@" not in email:
            skipped.append(raw_email)
            continue
        try:
            invite_data = await usecase.execute(
                slug,
                current_user.id,
                InviteMemberCommand(email=email, role=WorkspaceRole.STUDENT),
            )
            background_tasks.add_task(
                deliver_workspace_invitation_email_bg,
                email=invite_data["email"],
                workspace_name=invite_data["workspace_name"],
                role="STUDENT",
                invitation_url=invite_data["invitation_url"],
            )
            invited.append(email)
        except Exception:
            skipped.append(email)

    return {
        "message": f"Successfully queued invitations for {len(invited)} student(s)",
        "total_invited": len(invited),
        "invited": invited,
        "skipped": skipped,
    }


@router.post("/invitations/{token}/accept", status_code=200)
async def accept_invitation(
    token: str,
    request: AcceptInvitationRequest,
    usecase: AcceptInvitation = Depends(get_accept_invitation_usecase),
):
    result = await usecase.execute(token=token, password=request.password)
    return result


@router.get("/workspaces/{slug}/members")
async def get_workspace_members(
    slug: str,
    current_user=Depends(get_current_user),
    workspace_repo: WorkspaceRepo = Depends(get_workspace_repo),
    membership_repo: WorkspaceMembershipRepo = Depends(get_membership_repo),
):
    workspace = await workspace_repo.get_by_slug(slug)
    if workspace is None:
        raise WorkspaceNotFound()
    membership = await membership_repo.get_by_user_workspace(current_user.id, workspace.id)
    if membership is None:
        raise WorkspaceAccessDenied()
    members = await membership_repo.list_workspace_members(workspace.id)
    return members


@router.get("/workspaces/{slug}/teachers")
async def get_workspace_teachers(
    slug: str,
    current_user=Depends(get_current_user),
    workspace_repo: WorkspaceRepo = Depends(get_workspace_repo),
    membership_repo: WorkspaceMembershipRepo = Depends(get_membership_repo),
):
    workspace = await workspace_repo.get_by_slug(slug)
    if workspace is None:
        raise WorkspaceNotFound()
    membership = await membership_repo.get_by_user_workspace(current_user.id, workspace.id)
    if membership is None:
        raise WorkspaceAccessDenied()
    members = await membership_repo.list_workspace_members(workspace.id)
    teachers = [
        m for m in members
        if (m.get("role") in {WorkspaceRole.OWNER.value, WorkspaceRole.TEACHER.value, "OWNER", "TEACHER"})
    ]
    return teachers


@router.patch("/workspaces/{slug}/members/{user_id}/role")
async def update_member_role(
    slug: str,
    user_id: UUID,
    request: UpdateMemberRoleRequest,
    current_user=Depends(get_current_user),
    usecase: ChangeMemberRole = Depends(get_change_member_role_usecase),
):
    result = await usecase.execute(slug=slug, requester_id=current_user.id, target_user_id=user_id, new_role=request.role)
    return {"message": "Member role updated successfully", **result}


@router.post("/workspaces/{slug}/classrooms", status_code=201)
async def create_classroom(
    slug: str,
    request: CreateClassroomRequest,
    current_user=Depends(get_current_user),
    service: ClassroomService = Depends(get_classroom_service),
    workspace_repo=Depends(get_workspace_repo),
):
    workspace = await workspace_repo.get_by_slug(slug)
    if workspace is None:
        raise WorkspaceNotFound()
    classroom = await service.create(
        workspace,
        current_user.id,
        request.name,
        assigned_teacher_id=request.assigned_teacher_id,
    )
    return {
        "id": str(classroom.id),
        "name": classroom.name,
        "created_by_user_id": str(classroom.created_by_user_id),
        "assigned_teacher_id": str(classroom.assigned_teacher_id) if classroom.assigned_teacher_id else None,
    }


@router.get("/workspaces/{slug}/classrooms")
async def list_classrooms(
    slug: str,
    current_user=Depends(get_current_user),
    service: ClassroomService = Depends(get_classroom_service),
    workspace_repo=Depends(get_workspace_repo),
):
    workspace = await workspace_repo.get_by_slug(slug)
    if workspace is None:
        raise WorkspaceNotFound()
    classrooms = await service.list_classrooms(workspace.id, current_user.id)
    from app.modules.auth.infra.persistent.models.models import UserModel
    result = []
    for c in classrooms:
        assigned_email = None
        if c.assigned_teacher_id:
            assigned_user = await service.session.get(UserModel, c.assigned_teacher_id)
            if assigned_user:
                assigned_email = assigned_user.email
        result.append({
            "id": str(c.id),
            "name": c.name,
            "created_by_user_id": str(c.created_by_user_id),
            "assigned_teacher_id": str(c.assigned_teacher_id) if c.assigned_teacher_id else None,
            "assigned_teacher_email": assigned_email,
            "created_at": c.created_at.isoformat(),
        })
    return result


@router.post("/classrooms/{classroom_id}/invitations", status_code=201)
async def invite_student(
    classroom_id: UUID,
    request: InviteStudentRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    service: ClassroomService = Depends(get_classroom_service),
):
    invite_data = await service.invite_student(classroom_id, current_user.id, request.email)
    background_tasks.add_task(
        deliver_classroom_invitation_email_bg,
        email=invite_data["email"],
        classroom_name=invite_data["classroom_name"],
        invitation_url=invite_data["invitation_url"],
    )
    return {"message": "Student invitation sent", "invitation_url": invite_data["invitation_url"]}


@router.post("/classroom-invitations/{token}/accept", status_code=200)
async def accept_classroom_invitation(
    token: str,
    request: AcceptClassroomInvitationRequest,
):
    from app.infra.database.session import SessionLocal
    from app.infra.database.uow import uow_implementation
    from app.modules.workspace.application.usecase.classroom import ClassroomService
    from app.modules.auth.infra.persistent.repositories.sqlalchemy_outbox_repository import SQLAlchemyOutboxRepository
    async with SessionLocal() as session:
        uow = uow_implementation(session)
        outbox_repo = SQLAlchemyOutboxRepository(session)
        service = ClassroomService(session, outbox_repo, uow)
        result = await service.accept(token, request.password, request.roll_number)
    return result

