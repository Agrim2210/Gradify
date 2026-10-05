class DocumentDomainException(Exception):
    pass


class NoteNotFound(DocumentDomainException):
    pass


class ClassroomNotFound(DocumentDomainException):
    pass


class ClassroomAccessDenied(DocumentDomainException):
    pass


class InvalidFileTypeError(DocumentDomainException):
    pass


class FileUploadError(DocumentDomainException):
    pass
