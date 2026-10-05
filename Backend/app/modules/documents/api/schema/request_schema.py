from pydantic import BaseModel


class UploadNoteRequest(BaseModel):
    title: str
    description: str | None = None
