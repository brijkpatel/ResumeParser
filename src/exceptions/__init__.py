"""Init file for exceptions package."""

from .base_exception import ResumeParserException
from .api_exceptions import APIError, ExternalServiceError
from .parsing_exceptions import (
    FileParsingError,
    FieldExtractionError,
    UnsupportedFileFormatError,
    InvalidConfigurationError,
    StrategyExtractionError,
    InvalidStrategyConfigError,
    NoMatchFoundError,
)

__all__ = [
    "ResumeParserException",
    "APIError",
    "ExternalServiceError",
    "FileParsingError",
    "FieldExtractionError",
    "UnsupportedFileFormatError",
    "InvalidConfigurationError",
    "StrategyExtractionError",
    "InvalidStrategyConfigError",
    "NoMatchFoundError",
]

