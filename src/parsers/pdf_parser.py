"""PDF parser implementation using PDFMiner."""

from pathlib import Path
from typing import Union, List

from pdfminer.high_level import extract_text

from interfaces.file_parser import FileParser
from exceptions import FileParsingError
from utils import logger


class PDFParser(FileParser):
    """Concrete implementation of FileParser for PDF files.

    Uses PyPDF2 library to extract text content from PDF documents.
    Handles multiple pages and various PDF formats.
    """

    def __init__(self):
        """Initialize the PDF parser."""
        self.supported_extensions = [".pdf"]
        logger.debug("PDFParser initialized")

    def parse(self, file_path: str) -> str:
        """Parse PDF file and extract text content.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text content from the PDF

        Raises:
            FileParsingError: If parsing fails
        """
        self._validate_file_path(file_path)

        try:
            logger.info("Starting PDF parsing: %s", file_path)

            # Use PDFMiner's high-level API for simple text extraction
            text = extract_text(file_path)

            if not text or not text.strip():
                raise FileParsingError("No text content found in PDF.")

            # Clean up the extracted text
            cleaned_text = self._clean_extracted_text(text)

            logger.info(
                "Successfully parsed PDF: %s (%d characters)",
                file_path,
                len(cleaned_text),
            )
            return cleaned_text

        except FileParsingError:
            raise
        except Exception as e:
            raise FileParsingError("PDF parsing failed.", original_exception=e) from e

    def _clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted text.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove excessive whitespace while preserving line breaks
        lines: List[str] = []
        for line in text.split("\n"):
            # Clean each line but preserve structure
            cleaned_line = " ".join(line.split())
            if cleaned_line:  # Only add non-empty lines
                lines.append(cleaned_line)

        return "\n".join(lines)

    def supports_format(self, file_path: Union[str, Path]) -> bool:
        """Check if this parser supports the given file format.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is a PDF, False otherwise
        """
        extension = self._get_file_extension(file_path)
        return extension in self.supported_extensions
