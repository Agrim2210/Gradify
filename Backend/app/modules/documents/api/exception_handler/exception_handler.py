from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.modules.documents.domain.exception.exception import (
    ClassroomAccessDenied,
    ClassroomNotFound,
    FileUploadError,
    InvalidFileTypeError,
    NoteNotFound,
)


def register_document_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NoteNotFound)
    async def note_not_found_handler(request: Request, exc: NoteNotFound):
        return JSONResponse(status_code=404, content={"detail": "Note not found"})

    @app.exception_handler(ClassroomNotFound)
    async def classroom_not_found_handler(request: Request, exc: ClassroomNotFound):
        return JSONResponse(status_code=404, content={"detail": "Classroom not found"})

    @app.exception_handler(ClassroomAccessDenied)
    async def classroom_access_denied_handler(request: Request, exc: ClassroomAccessDenied):
        return JSONResponse(status_code=403, content={"detail": "Access denied to classroom"})

    @app.exception_handler(InvalidFileTypeError)
    async def invalid_file_type_handler(request: Request, exc: InvalidFileTypeError):
        return JSONResponse(status_code=400, content={"detail": "Only PDF files are allowed"})

    @app.exception_handler(FileUploadError)
    async def file_upload_error_handler(request: Request, exc: FileUploadError):
        return JSONResponse(status_code=502, content={"detail": str(exc)})
