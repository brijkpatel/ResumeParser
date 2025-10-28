"""Top-level framework facade for resume parsing.

This module provides the main entry point for the Resume Parser framework,
combining file parsing and field extraction into a single, easy-to-use interface.
"""

from pathlib import Path
from typing import Dict, Optional, List, Any

from interfaces import FileParser, FieldType, FieldExtractor
from coordinators import ResumeExtractor
from models import ResumeData
from parsers import PDFParser, WordParser
from extractors import create_extractor
from config import ExtractionConfig, DEFAULT_EXTRACTION_CONFIG
from exceptions import UnsupportedFileFormatError, FileParsingError
from utils import logger


class ResumeParserFramework:
    """Main framework facade for parsing resumes.

    This class combines file parsing (PDFParser, WordParser) with field
    extraction (ResumeExtractor) to provide a simple, unified interface
    for parsing resumes. It automatically determines the file type based
    on the file extension and uses the appropriate parser.

    The framework uses a configuration-driven approach to create field extractors
    with multiple fallback strategies for each field type.

    Design Pattern: Facade pattern
    - Provides a simple interface to a complex subsystem
    - Hides the complexity of file parsing and field extraction
    - Handles file type detection and parser selection
    - Creates extractors based on configuration

    Attributes:
        extractor: The ResumeExtractor coordinator for field extraction
        parsers: Dictionary mapping file extensions to FileParser instances
        config: Extraction configuration defining strategy preferences
    """

    # Supported file extensions
    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc"}

    def __init__(
        self,
        config: Optional[ExtractionConfig] = None,
        pdf_parser: Optional[FileParser] = None,
        word_parser: Optional[FileParser] = None,
    ):
        """Initialize the ResumeParserFramework.

        Args:
            config: Optional extraction configuration. Uses DEFAULT_EXTRACTION_CONFIG if None
            pdf_parser: Optional custom PDFParser (uses default if None)
            word_parser: Optional custom WordParser (uses default if None)
        """
        self.config = config or DEFAULT_EXTRACTION_CONFIG

        # Initialize parsers with defaults if not provided
        self.parsers: Dict[str, FileParser] = {
            ".pdf": pdf_parser or PDFParser(),
            ".docx": word_parser or WordParser(),
            ".doc": word_parser or WordParser(),  # .doc uses same parser as .docx
        }

        # Create extractors based on configuration
        self.extractor = self._create_extractor()

        logger.info(
            f"ResumeParserFramework initialized with {len(self.parsers)} parsers "
            f"and config-driven extractors"
        )

    def _create_extractor(self) -> ResumeExtractor:
        """Create a ResumeExtractor with extractors based on configuration.

        For each field type, creates multiple extractors based on the configured
        strategy preferences. These extractors will be tried in order.

        Returns:
            Configured ResumeExtractor with fallback extractors
        """
        logger.debug("Creating field extractors from configuration")

        extractors_dict: Dict[FieldType, List[FieldExtractor[Any]]] = {}

        for field_type in [FieldType.NAME, FieldType.EMAIL, FieldType.SKILLS]:
            strategies = self.config.get_strategies_for_field(field_type)
            field_extractors: List[FieldExtractor[Any]] = []

            logger.debug(
                f"Creating {len(strategies)} extractor(s) for {field_type.value}"
            )

            for strategy_type in strategies:
                try:
                    extractor = create_extractor(field_type, strategy_type)
                    field_extractors.append(extractor)
                    logger.debug(
                        f"Created {strategy_type.value} extractor for {field_type.value}"
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to create {strategy_type.value} extractor for "
                        f"{field_type.value}: {e}. Skipping this strategy."
                    )
                    continue

            if not field_extractors:
                logger.error(f"No extractors could be created for {field_type.value}")
                raise RuntimeError(
                    f"Failed to create any extractors for {field_type.value}"
                )

            extractors_dict[field_type] = field_extractors

        return ResumeExtractor(extractors_dict)

    def parse_resume(self, file_path: str) -> ResumeData:
        """Parse a resume file and extract structured information.

        This is the main entry point for the framework. It:
        1. Validates the file path and extension
        2. Selects the appropriate parser based on file extension
        3. Parses the file to extract text
        4. Uses the ResumeExtractor to extract fields
        5. Returns a ResumeData object with all extracted information

        Args:
            file_path: Path to the resume file (.pdf, .docx, or .doc)

        Returns:
            ResumeData object containing extracted name, email, and skills

        Raises:
            UnsupportedFileFormatError: If file extension is not supported
            FileParsingError: If file parsing fails
            FieldExtractionError: If field extraction fails
            FileNotFoundError: If the file does not exist
        """
        logger.info(f"Starting resume parsing for file: {file_path}")

        # Validate file exists
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"Resume file not found: {file_path}")

        if not path.is_file():
            logger.error(f"Path is not a file: {file_path}")
            raise ValueError(f"Path is not a file: {file_path}")

        # Determine file extension
        extension = path.suffix.lower()
        logger.debug(f"Detected file extension: {extension}")

        # Validate file extension
        if extension not in self.SUPPORTED_EXTENSIONS:
            logger.error(f"Unsupported file format: {extension}")
            raise UnsupportedFileFormatError(
                f"Unsupported file format: {extension}. "
                f"Supported formats: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}"
            )

        # Get the appropriate parser
        parser = self.parsers.get(extension)
        if not parser:
            logger.error(f"No parser found for extension: {extension}")
            raise UnsupportedFileFormatError(
                f"No parser configured for {extension} files"
            )

        logger.info(f"Using parser: {parser.__class__.__name__}")

        # Parse the file to extract text
        try:
            text = parser.parse(file_path)
            logger.info(f"Successfully parsed file, extracted {len(text)} characters")
        except Exception as e:
            logger.error(f"File parsing failed: {e}")
            raise FileParsingError(
                f"Failed to parse resume file: {file_path}", original_exception=e
            ) from e

        # Extract fields using the coordinator
        try:
            resume_data = self.extractor.extract(text)
            skills_count = len(resume_data.skills) if resume_data.skills else 0
            logger.info(
                f"Successfully extracted resume data: {resume_data.name}, "
                f"{resume_data.email}, {skills_count} skills"
            )
            return resume_data
        except Exception as e:
            logger.error(f"Field extraction failed: {e}")
            raise

    def is_supported_file(self, file_path: str) -> bool:
        """Check if a file format is supported.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file format is supported, False otherwise
        """
        extension = Path(file_path).suffix.lower()
        return extension in self.SUPPORTED_EXTENSIONS

    def get_supported_extensions(self) -> set[str]:
        """Get the set of supported file extensions.

        Returns:
            Set of supported file extensions (e.g., {'.pdf', '.docx', '.doc'})
        """
        return self.SUPPORTED_EXTENSIONS.copy()
