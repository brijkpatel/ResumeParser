from exceptions.base_exception import ResumeParserException


class APIError(ResumeParserException):
    """Exception raised when external API calls fail."""