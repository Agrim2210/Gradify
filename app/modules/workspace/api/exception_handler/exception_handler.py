from fastapi import Request
from fastapi.responses import JSONResponse

from app.modules.workspace.domain.exception.exception import (
    InvitationEmailMismatch,
    InvitationExpired,
    InvitationNotFound,
    MembershipAlreadyExists,
    WorkspaceAccessDenied,
    WorkspaceNotFound,
)


async def workspace_not_found_handler(request: Request, exc: WorkspaceNotFound) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": "Workspace not found"})


async def workspace_access_denied_handler(request: Request, exc: WorkspaceAccessDenied) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": "Workspace access denied"})


async def invitation_not_found_handler(request: Request, exc: InvitationNotFound) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": "Invitation not found or invalid"})


async def invitation_expired_handler(request: Request, exc: InvitationExpired) -> JSONResponse:
    return JSONResponse(status_code=410, content={"detail": "Invitation has expired"})


async def invitation_email_mismatch_handler(request: Request, exc: InvitationEmailMismatch) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": "Invitation email mismatch"})


async def membership_exists_handler(request: Request, exc: MembershipAlreadyExists) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": "Workspace membership already exists"})


def register_workspace_exception_handlers(app) -> None:
    app.add_exception_handler(WorkspaceNotFound, workspace_not_found_handler)
    app.add_exception_handler(WorkspaceAccessDenied, workspace_access_denied_handler)
    app.add_exception_handler(InvitationNotFound, invitation_not_found_handler)
    app.add_exception_handler(InvitationExpired, invitation_expired_handler)
    app.add_exception_handler(InvitationEmailMismatch, invitation_email_mismatch_handler)
    app.add_exception_handler(MembershipAlreadyExists, membership_exists_handler)
