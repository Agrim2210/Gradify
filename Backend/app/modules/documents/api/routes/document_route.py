from uuid import UUID
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from app.modules.auth.bootstrap.dependencies import get_current_user
from app.modules.auth.infra.tasks.email_tasks import deliver_note_upload_notification_bg
from app.modules.documents.api.schema.response_schema import NoteResponse
from app.modules.documents.application.dto.note_dto import UploadNoteCommand
from app.modules.documents.application.usecase.get_note_usecase import GetNoteUseCase
from app.modules.documents.application.usecase.list_notes_usecase import ListNotesUseCase
from app.modules.documents.application.usecase.upload_note_usecase import UploadNoteUseCase
from app.modules.documents.bootstrap.dependencies import (
    get_note_usecase,
    get_list_notes_usecase,
    get_upload_note_usecase,
    get_assignment_service,
)

router = APIRouter(tags=["Documents"])


@router.post("/classrooms/{classroom_id}/notes", response_model=NoteResponse, status_code=201)
async def upload_note(
    classroom_id: UUID,
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    description: str | None = Form(None),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    usecase: UploadNoteUseCase = Depends(get_upload_note_usecase),
):
    command = UploadNoteCommand(
        classroom_id=classroom_id,
        user_id=current_user.id,
        title=title,
        description=description,
        file_name=file.filename or "notes.pdf",
        content_type=file.content_type or "application/pdf",
        file_size=file.size or 0,
        file_obj=file.file,
    )
    result = await usecase.execute(command)
    if result.student_emails:
        background_tasks.add_task(
            deliver_note_upload_notification_bg,
            student_emails=result.student_emails,
            classroom_name=result.classroom_name or "Classroom",
            note_title=result.title,
            note_url=result.view_url or "",
        )
    return NoteResponse(
        id=result.id,
        classroom_id=result.classroom_id,
        uploaded_by_user_id=result.uploaded_by_user_id,
        title=result.title,
        description=result.description,
        file_name=result.file_name,
        file_size=result.file_size,
        mime_type=result.mime_type,
        created_at=result.created_at,
        view_url=result.view_url,
        download_url=result.download_url,
    )


@router.get("/classrooms/{classroom_id}/notes", response_model=list[NoteResponse])
async def list_notes(
    classroom_id: UUID,
    current_user=Depends(get_current_user),
    usecase: ListNotesUseCase = Depends(get_list_notes_usecase),
):
    results = await usecase.execute(classroom_id, current_user.id)
    return [
        NoteResponse(
            id=item.id,
            classroom_id=item.classroom_id,
            uploaded_by_user_id=item.uploaded_by_user_id,
            title=item.title,
            description=item.description,
            file_name=item.file_name,
            file_size=item.file_size,
            mime_type=item.mime_type,
            created_at=item.created_at,
            view_url=item.view_url,
            download_url=item.download_url,
        )
        for item in results
    ]


@router.get("/classrooms/{classroom_id}/notes/{note_id}", response_model=NoteResponse)
async def get_note(
    classroom_id: UUID,
    note_id: UUID,
    current_user=Depends(get_current_user),
    usecase: GetNoteUseCase = Depends(get_note_usecase),
):
    result = await usecase.execute(classroom_id, note_id, current_user.id)
    return NoteResponse(
        id=result.id,
        classroom_id=result.classroom_id,
        uploaded_by_user_id=result.uploaded_by_user_id,
        title=result.title,
        description=result.description,
        file_name=result.file_name,
        file_size=result.file_size,
        mime_type=result.mime_type,
        created_at=result.created_at,
        view_url=result.view_url,
        download_url=result.download_url,
    )


@router.get("/classrooms/{classroom_id}/notes/{note_id}/view")
async def view_note(
    classroom_id: UUID,
    note_id: UUID,
    current_user=Depends(get_current_user),
    usecase: GetNoteUseCase = Depends(get_note_usecase),
):
    result = await usecase.execute(classroom_id, note_id, current_user.id)
    return RedirectResponse(url=result.view_url, status_code=307)


@router.get("/classrooms/{classroom_id}/notes/{note_id}/download")
async def download_note(
    classroom_id: UUID,
    note_id: UUID,
    current_user=Depends(get_current_user),
    usecase: GetNoteUseCase = Depends(get_note_usecase),
):
    result = await usecase.execute(classroom_id, note_id, current_user.id)
    return RedirectResponse(url=result.download_url, status_code=307)


@router.post("/classrooms/{classroom_id}/assignments", status_code=201)
async def create_assignment(
    classroom_id: UUID,
    title: str = Form(...),
    description: str | None = Form(None),
    due_at: str | None = Form(None),
    file: UploadFile | None = File(None),
    current_user=Depends(get_current_user),
    svc=Depends(get_assignment_service),
):
    result = await svc.create_assignment(
        classroom_id=classroom_id,
        teacher_user_id=current_user.id,
        title=title,
        description=description,
        due_at=due_at,
        file=file,
    )
    return result


@router.get("/classrooms/{classroom_id}/assignments")
async def list_assignments(
    classroom_id: UUID,
    current_user=Depends(get_current_user),
    svc=Depends(get_assignment_service),
):
    return await svc.list_assignments(classroom_id, current_user.id)


@router.post("/classrooms/{classroom_id}/assignments/{assignment_id}/submissions", status_code=201)
async def submit_assignment(
    classroom_id: UUID,
    assignment_id: UUID,
    roll_number: str | None = Form(None),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    svc=Depends(get_assignment_service),
):
    return await svc.submit_assignment(
        classroom_id=classroom_id,
        assignment_id=assignment_id,
        student_user_id=current_user.id,
        file=file,
        roll_number=roll_number,
    )


@router.get("/classrooms/{classroom_id}/assignments/{assignment_id}/submissions")
async def list_submissions(
    classroom_id: UUID,
    assignment_id: UUID,
    current_user=Depends(get_current_user),
    svc=Depends(get_assignment_service),
):
    return await svc.list_submissions(classroom_id, assignment_id, current_user.id)


class GradeSubmissionRequest(BaseModel):
    student_user_id: UUID
    score: float = Field(..., ge=0)
    feedback: str | None = None


@router.get("/classrooms/{classroom_id}/student-overview")
async def get_student_overview(
    classroom_id: UUID,
    current_user=Depends(get_current_user),
    svc=Depends(get_assignment_service),
):
    return await svc.get_student_overview(classroom_id, current_user.id)


@router.get("/classrooms/{classroom_id}/assignments/{assignment_id}/categorized-submissions")
async def get_categorized_submissions(
    classroom_id: UUID,
    assignment_id: UUID,
    current_user=Depends(get_current_user),
    svc=Depends(get_assignment_service),
):
    return await svc.get_categorized_submissions(classroom_id, assignment_id, current_user.id)


@router.post("/classrooms/{classroom_id}/assignments/{assignment_id}/grade")
async def grade_submission(
    classroom_id: UUID,
    assignment_id: UUID,
    body: GradeSubmissionRequest,
    current_user=Depends(get_current_user),
    svc=Depends(get_assignment_service),
):
    return await svc.grade_submission(
        classroom_id=classroom_id,
        assignment_id=assignment_id,
        requester_id=current_user.id,
        student_user_id=body.student_user_id,
        score=body.score,
        feedback=body.feedback,
    )


@router.get("/classrooms/{classroom_id}/gradebook")
async def get_classroom_gradebook(
    classroom_id: UUID,
    current_user=Depends(get_current_user),
    svc=Depends(get_assignment_service),
):
    return await svc.get_classroom_gradebook(classroom_id, current_user.id)

