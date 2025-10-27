"""Abstract base class for file parsers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

from exceptions import FileParsingError
from utils import logger


class FileParser(ABC):
    """Abstract base class for file parsers following the Strategy pattern.

    This interface defines the contract for parsing different file formats.
    Concrete implementations should handle specific file formats like PDF, Word, etc.
    """

    @abstractmethod
    def parse(self, file_path: Union[str, Path]) -> str:
        """Parse a file and extract its text content.

        Args:
            file_path: Path to the file to parse

        Returns:
            Extracted text content from the file

        Raises:
            FileParsingError: If parsing fails
            UnsupportedFileFormatError: If file format is not supported
            FileNotFoundError: If file does not exist
        """

    @abstractmethod
    def supports_format(self, file_path: Union[str, Path]) -> bool:
        """Check if this parser supports the given file format.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the parser supports this file format, False otherwise
        """

    def _validate_file_path(self, file_path: Union[str, Path]) -> Path:
        """Validate that the file path exists and is readable.

        Args:
            file_path: Path to validate

        Returns:
            Validated Path object

        Raises:
            FileNotFoundError: If file does not exist
            PermissionError: If file is not readable
        """
        path_obj = Path(file_path)

        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {path_obj}")

        if not path_obj.is_file():
            raise FileParsingError(f"Path is not a file: {path_obj}")

        if not path_obj.stat().st_size > 0:
            logger.warning("File appears to be empty: %s", path_obj)

        # Check if file is readable
        try:
            with open(path_obj, "rb") as f:
                f.read(1)  # Try to read one byte
        except PermissionError as exc:
            raise PermissionError(f"File is not readable: {path_obj}") from exc

        return path_obj

    def _get_file_extension(self, file_path: Union[str, Path]) -> str:
        """Get the file extension in lowercase.

        Args:
            file_path: Path to get extension from

        Returns:
            File extension in lowercase (including the dot)
        """
        return Path(file_path).suffix.lower()
