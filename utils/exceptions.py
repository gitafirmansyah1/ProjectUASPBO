class AppBaseException(Exception):
    """Base exception for application."""
    def __init__(self, message: str = "", details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

class DatabaseConnectionError(AppBaseException):
    pass

class DatabaseQueryError(AppBaseException):
    pass

class DatabaseTransactionError(AppBaseException):
    pass

class FileValidationError(AppBaseException):
    pass

class FileUploadError(AppBaseException):
    pass

class PDFExtractionError(AppBaseException):
    pass

class PDFTableNotFoundError(PDFExtractionError):
    pass

class ValidationExecutionError(AppBaseException):
    pass

class ValidationError(AppBaseException):
    pass

class ReportGenerationError(AppBaseException):
    pass

class TextCleaningError(AppBaseException):
    pass

class DuplicateMeetingError(AppBaseException):
    pass

class MeetingNumberExceededError(AppBaseException):
    pass
