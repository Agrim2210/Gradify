import io
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import pytest
from app.modules.auth.application.dto.outbox_dto import Payload
from app.modules.auth.application.enums.outbox_enum import EventType
from app.modules.documents.application.dto.note_dto import UploadNoteCommand
from app.modules.documents.application.usecase.get_note_usecase import GetNoteUseCase
from app.modules.documents.application.usecase.list_notes_usecase import ListNotesUseCase
from app.modules.documents.application.usecase.upload_note_usecase import UploadNoteUseCase
from app.modules.documents.domain.entities.note import Note
from app.modules.documents.domain.exception.exception import (
    ClassroomAccessDenied,
    ClassroomNotFound,
    InvalidFileTypeError,
    NoteNotFound,
)
from app.modules.documents.infra.storage.backblaze_storage_service import BackblazeB2StorageService
from app.modules.workspace.domain.enums.classroom_role import ClassroomRole
from app.modules.workspace.domain.enums.workspace_role import WorkspaceRole
from app.modules.workspace.infra.database.classroom_models import ClassroomMembershipModel, ClassroomModel
from app.shared.infra.email.smtp_email_sender import SMTPEmailSender


@pytest.mark.asyncio
async def test_upload_note_rejects_non_pdf():
    session = AsyncMock()
    note_repo = AsyncMock()
    storage_service = MagicMock()
    outbox_repo = MagicMock()
    uow = AsyncMock()

    usecase = UploadNoteUseCase(session, note_repo, storage_service, outbox_repo, uow)
    command = UploadNoteCommand(
        classroom_id=uuid4(),
        user_id=uuid4(),
        title="Lecture 1",
        description="Intro",
        file_name="lecture.txt",
        content_type="text/plain",
        file_size=100,
        file_obj=io.BytesIO(b"hello"),
    )

    with pytest.raises(InvalidFileTypeError):
        await usecase.execute(command)


@pytest.mark.asyncio
async def test_upload_note_classroom_not_found():
    session = AsyncMock()
    session.get.return_value = None
    note_repo = AsyncMock()
    storage_service = MagicMock()
    outbox_repo = MagicMock()
    uow = AsyncMock()

    usecase = UploadNoteUseCase(session, note_repo, storage_service, outbox_repo, uow)
    command = UploadNoteCommand(
        classroom_id=uuid4(),
        user_id=uuid4(),
        title="Lecture 1",
        description="Intro",
        file_name="lecture.pdf",
        content_type="application/pdf",
        file_size=100,
        file_obj=io.BytesIO(b"%PDF-1.4"),
    )

    with pytest.raises(ClassroomNotFound):
        await usecase.execute(command)


@pytest.mark.asyncio
async def test_upload_note_access_denied_if_not_owner():
    classroom_id = uuid4()
    user_id = uuid4()
    classroom = ClassroomModel(
        id=classroom_id,
        workspace_id=uuid4(),
        name="Physics 101",
        created_by_user_id=uuid4(),
        created_at=datetime.now(timezone.utc),
    )

    session = AsyncMock()
    session.get.return_value = classroom

    membership_mock = MagicMock()
    membership_mock.scalar_one_or_none.return_value = ClassroomMembershipModel(
        id=uuid4(),
        classroom_id=classroom_id,
        user_id=user_id,
        role=ClassroomRole.STUDENT,
        created_at=datetime.now(timezone.utc),
    )
    session.execute.return_value = membership_mock

    note_repo = AsyncMock()
    storage_service = MagicMock()
    outbox_repo = MagicMock()
    uow = AsyncMock()

    usecase = UploadNoteUseCase(session, note_repo, storage_service, outbox_repo, uow)
    command = UploadNoteCommand(
        classroom_id=classroom_id,
        user_id=user_id,
        title="Lecture 1",
        description="Intro",
        file_name="lecture.pdf",
        content_type="application/pdf",
        file_size=100,
        file_obj=io.BytesIO(b"%PDF-1.4"),
    )

    with pytest.raises(ClassroomAccessDenied):
        await usecase.execute(command)


@pytest.mark.asyncio
async def test_upload_note_success_with_student_outbox_events():
    classroom_id = uuid4()
    teacher_id = uuid4()
    classroom = ClassroomModel(
        id=classroom_id,
        workspace_id=uuid4(),
        name="Chemistry 101",
        created_by_user_id=teacher_id,
        created_at=datetime.now(timezone.utc),
    )

    teacher_membership = ClassroomMembershipModel(
        id=uuid4(),
        classroom_id=classroom_id,
        user_id=teacher_id,
        role=ClassroomRole.OWNER,
        created_at=datetime.now(timezone.utc),
    )

    session = AsyncMock()
    session.get.return_value = classroom

    membership_result = MagicMock()
    membership_result.scalar_one_or_none.return_value = teacher_membership

    students_result = MagicMock()
    students_scalars = MagicMock()
    students_scalars.all.return_value = ["student1@example.com", "student2@example.com"]
    students_result.scalars.return_value = students_scalars

    session.execute.side_effect = [membership_result, students_result]

    note_repo = AsyncMock()
    storage_service = MagicMock()
    storage_service.upload_file = AsyncMock()
    storage_service.generate_presigned_view_url.return_value = "https://b2.test/view"
    storage_service.generate_presigned_download_url.return_value = "https://b2.test/download"

    outbox_repo = MagicMock()
    outbox_repo.add = MagicMock()

    uow = AsyncMock()

    usecase = UploadNoteUseCase(session, note_repo, storage_service, outbox_repo, uow)
    command = UploadNoteCommand(
        classroom_id=classroom_id,
        user_id=teacher_id,
        title="Organic Chem Notes",
        description="Chapter 1 notes",
        file_name="chapter1.pdf",
        content_type="application/pdf",
        file_size=1024,
        file_obj=io.BytesIO(b"%PDF-1.4 sample content"),
    )

    result = await usecase.execute(command)

    assert result.title == "Organic Chem Notes"
    assert result.classroom_id == classroom_id
    assert result.uploaded_by_user_id == teacher_id
    assert result.view_url == "https://b2.test/view"
    assert result.download_url == "https://b2.test/download"

    storage_service.upload_file.assert_awaited_once()
    note_repo.save.assert_awaited_once()
    assert outbox_repo.add.call_count == 2
    uow.commit.assert_awaited_once()

    first_event = outbox_repo.add.call_args_list[0][0][0]
    assert first_event.event_type == EventType.NOTE_UPLOADED
    assert first_event.payload.email == "student1@example.com"
    assert first_event.payload.classroom_name == "Chemistry 101"
    assert first_event.payload.note_title == "Organic Chem Notes"


@pytest.mark.asyncio
async def test_list_notes_success():
    classroom_id = uuid4()
    student_id = uuid4()
    classroom = ClassroomModel(
        id=classroom_id,
        workspace_id=uuid4(),
        name="Math 101",
        created_by_user_id=uuid4(),
        created_at=datetime.now(timezone.utc),
    )

    session = AsyncMock()
    session.get.return_value = classroom

    ws_mem = MagicMock()
    ws_mem.role = WorkspaceRole.STUDENT
    membership_mock = MagicMock()
    membership_mock.scalar_one_or_none.return_value = ws_mem
    session.execute.return_value = membership_mock

    note_repo = AsyncMock()
    note_repo.list_by_classroom_id.return_value = [
        Note(
            id=uuid4(),
            classroom_id=classroom_id,
            uploaded_by_user_id=uuid4(),
            title="Calculus I",
            description="Week 1",
            file_name="calc1.pdf",
            file_key="key1",
            file_size=500,
            mime_type="application/pdf",
            created_at=datetime.now(timezone.utc),
        )
    ]

    storage_service = MagicMock()
    storage_service.generate_presigned_view_url.return_value = "https://b2.test/view"
    storage_service.generate_presigned_download_url.return_value = "https://b2.test/download"

    usecase = ListNotesUseCase(session, note_repo, storage_service)
    notes = await usecase.execute(classroom_id, student_id)

    assert len(notes) == 1
    assert notes[0].title == "Calculus I"
    assert notes[0].view_url == "https://b2.test/view"
    assert notes[0].download_url == "https://b2.test/download"


@pytest.mark.asyncio
async def test_get_note_success():
    classroom_id = uuid4()
    note_id = uuid4()
    student_id = uuid4()
    classroom = ClassroomModel(
        id=classroom_id,
        workspace_id=uuid4(),
        name="Bio 101",
        created_by_user_id=uuid4(),
        created_at=datetime.now(timezone.utc),
    )

    session = AsyncMock()
    session.get.return_value = classroom

    ws_mem = MagicMock()
    ws_mem.role = WorkspaceRole.STUDENT
    membership_mock = MagicMock()
    membership_mock.scalar_one_or_none.return_value = ws_mem
    session.execute.return_value = membership_mock

    note_repo = AsyncMock()
    note_repo.get_by_id.return_value = Note(
        id=note_id,
        classroom_id=classroom_id,
        uploaded_by_user_id=uuid4(),
        title="Genetics",
        description="Lecture 3",
        file_name="genetics.pdf",
        file_key="key_genetics",
        file_size=600,
        mime_type="application/pdf",
        created_at=datetime.now(timezone.utc),
    )

    storage_service = MagicMock()
    storage_service.generate_presigned_view_url.return_value = "https://b2.test/view"
    storage_service.generate_presigned_download_url.return_value = "https://b2.test/download"

    usecase = GetNoteUseCase(session, note_repo, storage_service)
    note = await usecase.execute(classroom_id, note_id, student_id)

    assert note.id == note_id
    assert note.title == "Genetics"
    assert note.view_url == "https://b2.test/view"
    assert note.download_url == "https://b2.test/download"


@pytest.mark.asyncio
async def test_get_note_not_found():
    classroom_id = uuid4()
    student_id = uuid4()
    classroom = ClassroomModel(
        id=classroom_id,
        workspace_id=uuid4(),
        name="Bio 101",
        created_by_user_id=uuid4(),
        created_at=datetime.now(timezone.utc),
    )

    session = AsyncMock()
    session.get.return_value = classroom

    ws_mem = MagicMock()
    ws_mem.role = WorkspaceRole.STUDENT
    membership_mock = MagicMock()
    membership_mock.scalar_one_or_none.return_value = ws_mem
    session.execute.return_value = membership_mock

    note_repo = AsyncMock()
    note_repo.get_by_id.return_value = None

    storage_service = MagicMock()

    usecase = GetNoteUseCase(session, note_repo, storage_service)
    with pytest.raises(NoteNotFound):
        await usecase.execute(classroom_id, uuid4(), student_id)


def test_backblaze_presigned_url_generation():
    service = BackblazeB2StorageService(
        endpoint_url="https://s3.us-west-004.backblazeb2.com",
        key_id="test_key_id",
        application_key="test_app_key",
        bucket_name="my-bucket",
        region_name="us-west-004",
    )

    client_mock = MagicMock()
    client_mock.generate_presigned_url.return_value = "https://signed.url"
    service._get_client = MagicMock(return_value=client_mock)

    view_url = service.generate_presigned_view_url("test_key")
    assert view_url == "https://signed.url"
    client_mock.generate_presigned_url.assert_called_with(
        "get_object",
        Params={
            "Bucket": "my-bucket",
            "Key": "test_key",
            "ResponseContentType": "application/pdf",
            "ResponseContentDisposition": "inline",
        },
        ExpiresIn=3600,
    )

    download_url = service.generate_presigned_download_url("test_key", "doc.pdf")
    assert download_url == "https://signed.url"
    client_mock.generate_presigned_url.assert_called_with(
        "get_object",
        Params={
            "Bucket": "my-bucket",
            "Key": "test_key",
            "ResponseContentDisposition": 'attachment; filename="doc.pdf"',
        },
        ExpiresIn=3600,
    )


@pytest.mark.asyncio
async def test_smtp_email_sender_formats_note_notification():
    sender = SMTPEmailSender(
        host="smtp.example.com",
        port=587,
        username="bot@example.com",
        password="password",
        sender_email="bot@example.com",
    )

    payload = Payload(
        email="student@example.com",
        classroom_name="Physics 101",
        note_title="Mechanics Notes",
        note_url="http://localhost:3000/classrooms/123/notes",
    )

    sent_messages = []

    async def fake_send(msg, **kwargs):
        sent_messages.append(msg)

    import aiosmtplib
    original_send = aiosmtplib.send
    aiosmtplib.send = fake_send
    try:
        await sender.send_email(payload)
        assert len(sent_messages) == 1
        msg = sent_messages[0]
        assert msg["to"] == "student@example.com"
        assert msg["Subject"] == "New notes uploaded in Physics 101: Mechanics Notes"
        body = msg.get_content()
        assert "Mechanics Notes" in body
        assert "Physics 101" in body
        assert "http://localhost:3000/classrooms/123/notes" in body
    finally:
        aiosmtplib.send = original_send
