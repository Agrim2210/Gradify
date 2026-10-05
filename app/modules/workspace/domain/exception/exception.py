class WorkspaceNameRequired(Exception):
    ...
class WorkspaceSlugExists(Exception):
    ...
class WorkspaceArchived(Exception):
    ...


class WorkspaceNotFound(Exception):
    ...


class WorkspaceAccessDenied(Exception):
    ...


class InvitationNotFound(Exception):
    ...


class InvitationExpired(Exception):
    ...


class InvitationEmailMismatch(Exception):
    ...


class MembershipAlreadyExists(Exception):
    ...
            
