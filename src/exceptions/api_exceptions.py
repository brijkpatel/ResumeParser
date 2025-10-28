from exceptions.base_exception import ResumeParserException


class APIError(ResumeParserException):
    """Exception raised when external API calls fail."""


class ExternalServiceError(APIError):
    """Raised when an external service (like LLM API, Gliner, etc.) fails."""
