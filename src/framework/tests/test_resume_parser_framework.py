"""Tests for ResumeParserFramework."""

import pytest
from unittest.mock import Mock, patch

from framework.resume_parser_framework import ResumeParserFramework
from coordinators import ResumeExtractor
from interfaces import FileParser, FieldType, StrategyType
from models import ResumeData
from config import ExtractionConfig
from exceptions import (
    UnsupportedFileFormatError,
    FileParsingError,
    FieldExtractionError,
)


class TestResumeParserFrameworkInitialization:
    """Test cases for ResumeParserFramework initialization."""

    @patch.object(ResumeParserFramework, "_create_extractor")
    def test_initialization_with_default_config(self, mock_create_extractor: Mock) -> None:
        """Test successful initialization with default configuration."""
        # Arrange - mock the factory to avoid actual model loading
        mock_extractor = Mock()
        mock_create_extractor.return_value = mock_extractor

        # Act
        framework = ResumeParserFramework()

        # Assert
        assert framework.extractor is not None
        assert len(framework.parsers) == 3
        assert ".pdf" in framework.parsers
        assert ".docx" in framework.parsers
        assert ".doc" in framework.parsers
        assert framework.config is not None

    @patch.object(ResumeParserFramework, "_create_extractor")
    def test_initialization_with_custom_parsers(self, mock_create_extractor: Mock) -> None:
        """Test initialization with custom parsers."""
        # Arrange
        mock_extractor = Mock()
        mock_create_extractor.return_value = mock_extractor
        pdf_parser = Mock(spec=FileParser)
        word_parser = Mock(spec=FileParser)

        # Act
        framework = ResumeParserFramework(
            pdf_parser=pdf_parser, word_parser=word_parser
        )

        # Assert
        assert framework.parsers[".pdf"] == pdf_parser
        assert framework.parsers[".docx"] == word_parser
        assert framework.parsers[".doc"] == word_parser

    @patch.object(ResumeParserFramework, "_create_extractor")
    def test_initialization_with_custom_config(self, mock_create_extractor: Mock) -> None:
        """Test initialization with custom configuration."""
        # Arrange
        mock_extractor = Mock()
        mock_create_extractor.return_value = mock_extractor
        
        custom_config = ExtractionConfig(
            strategy_preferences={
                FieldType.NAME: [StrategyType.NER],
                FieldType.EMAIL: [StrategyType.REGEX],
                FieldType.SKILLS: [StrategyType.NER],
            }
        )

        # Act
        framework = ResumeParserFramework(config=custom_config)

        # Assert
        assert framework.config == custom_config
        assert framework.extractor is not None


class TestResumeParserFrameworkParseResume:
    """Test cases for parse_resume method."""

    @patch.object(ResumeParserFramework, "_create_extractor")
    @patch("framework.resume_parser_framework.Path")
    def test_parse_pdf_resume_success(self, mock_path_class: Mock, mock_create_extractor_method: Mock) -> None:
        """Test successful parsing of PDF resume."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".pdf"
        mock_path_class.return_value = mock_path

        # Create actual ResumeData instead of mocking
        resume_data = ResumeData(
            name="John Doe", email="john@example.com", skills=["Python"]
        )
        
        mock_extractor = Mock()
        mock_extractor.extract = Mock(return_value=resume_data)
        mock_create_extractor_method.return_value = mock_extractor

        pdf_parser = Mock(spec=FileParser)
        pdf_parser.parse.return_value = "Resume text content"

        framework = ResumeParserFramework(pdf_parser=pdf_parser)

        # Act
        result = framework.parse_resume("/path/to/resume.pdf")

        # Assert
        assert result == resume_data
        pdf_parser.parse.assert_called_once_with("/path/to/resume.pdf")
        mock_extractor.extract.assert_called_once_with("Resume text content")

    @patch.object(ResumeParserFramework, "_create_extractor")
    @patch("framework.resume_parser_framework.Path")
    def test_parse_docx_resume_success(self, mock_path_class: Mock, mock_create_extractor: Mock) -> None:
        """Test successful parsing of DOCX resume."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".docx"
        mock_path_class.return_value = mock_path

        resume_data = ResumeData(
            name="Jane Smith", email="jane@example.com", skills=["Java"]
        )
        
        mock_extractor = Mock()
        mock_extractor.extract = Mock(return_value=resume_data)
        mock_create_extractor.return_value = mock_extractor

        word_parser = Mock(spec=FileParser)
        word_parser.parse.return_value = "DOCX resume text"

        framework = ResumeParserFramework(word_parser=word_parser)

        # Act
        result = framework.parse_resume("/path/to/resume.docx")

        # Assert
        assert result == resume_data
        word_parser.parse.assert_called_once_with("/path/to/resume.docx")

    @patch.object(ResumeParserFramework, "_create_extractor")
    @patch("framework.resume_parser_framework.Path")
    def test_parse_doc_resume_success(self, mock_path_class: Mock, mock_create_extractor: Mock) -> None:
        """Test successful parsing of DOC resume."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".doc"
        mock_path_class.return_value = mock_path

        resume_data = ResumeData(
            name="Bob Johnson", email="bob@example.com", skills=["SQL"]
        )
        
        mock_extractor = Mock()
        mock_extractor.extract = Mock(return_value=resume_data)
        mock_create_extractor.return_value = mock_extractor

        word_parser = Mock(spec=FileParser)
        word_parser.parse.return_value = "DOC resume text"

        framework = ResumeParserFramework(word_parser=word_parser)

        # Act
        result = framework.parse_resume("/path/to/resume.doc")

        # Assert
        assert result == resume_data
        word_parser.parse.assert_called_once_with("/path/to/resume.doc")

    @patch.object(ResumeParserFramework, "_create_extractor")
    @patch("framework.resume_parser_framework.Path")
    def test_parse_resume_with_uppercase_extension(self, mock_path_class: Mock, mock_create_extractor: Mock) -> None:
        """Test parsing resume with uppercase file extension."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".PDF"
        mock_path_class.return_value = mock_path

        resume_data = ResumeData(
            name="Alice", email="alice@example.com", skills=["Python"]
        )
        
        mock_extractor = Mock()
        mock_extractor.extract = Mock(return_value=resume_data)
        mock_create_extractor.return_value = mock_extractor

        pdf_parser = Mock(spec=FileParser)
        pdf_parser.parse.return_value = "Resume text"

        framework = ResumeParserFramework(pdf_parser=pdf_parser)

        # Act
        result = framework.parse_resume("/path/to/RESUME.PDF")

        # Assert
        assert result == resume_data


class TestResumeParserFrameworkFileValidation:
    """Test cases for file validation."""

    @patch.object(ResumeParserFramework, "_create_extractor")
    @patch("framework.resume_parser_framework.Path")
    def test_parse_nonexistent_file_raises_error(self, mock_path_class: Mock, mock_create_extractor: Mock) -> None:
        """Test that non-existent file raises FileNotFoundError."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = False
        mock_path_class.return_value = mock_path

        mock_extractor = Mock(spec=ResumeExtractor)
        mock_create_extractor.return_value = mock_extractor
        framework = ResumeParserFramework()

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Resume file not found"):
            framework.parse_resume("/path/to/nonexistent.pdf")

    @patch.object(ResumeParserFramework, "_create_extractor")
    @patch("framework.resume_parser_framework.Path")
    def test_parse_directory_raises_error(self, mock_path_class: Mock, mock_create_extractor: Mock) -> None:
        """Test that directory path raises ValueError."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = False
        mock_path_class.return_value = mock_path

        mock_extractor = Mock(spec=ResumeExtractor)
        mock_create_extractor.return_value = mock_extractor
        framework = ResumeParserFramework()

        # Act & Assert
        with pytest.raises(ValueError, match="Path is not a file"):
            framework.parse_resume("/path/to/directory")

    @patch.object(ResumeParserFramework, "_create_extractor")
    @patch("framework.resume_parser_framework.Path")
    def test_parse_unsupported_extension_raises_error(self, mock_path_class: Mock, mock_create_extractor: Mock) -> None:
        """Test that unsupported file extension raises UnsupportedFileFormatError."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".txt"
        mock_path_class.return_value = mock_path

        mock_extractor = Mock(spec=ResumeExtractor)
        mock_create_extractor.return_value = mock_extractor
        framework = ResumeParserFramework()

        # Act & Assert
        with pytest.raises(
            UnsupportedFileFormatError, match="Unsupported file format: .txt"
        ):
            framework.parse_resume("/path/to/resume.txt")

    @patch.object(ResumeParserFramework, "_create_extractor")
    @patch("framework.resume_parser_framework.Path")
    def test_parse_no_extension_raises_error(self, mock_path_class: Mock, mock_create_extractor: Mock) -> None:
        """Test that file with no extension raises UnsupportedFileFormatError."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ""
        mock_path_class.return_value = mock_path

        mock_extractor = Mock(spec=ResumeExtractor)
        mock_create_extractor.return_value = mock_extractor
        framework = ResumeParserFramework()

        # Act & Assert
        with pytest.raises(UnsupportedFileFormatError):
            framework.parse_resume("/path/to/resume")


class TestResumeParserFrameworkErrorHandling:
    """Test cases for error handling."""

    @patch.object(ResumeParserFramework, "_create_extractor")
    @patch("framework.resume_parser_framework.Path")
    def test_parser_failure_raises_file_parsing_error(self, mock_path_class: Mock, mock_create_extractor: Mock) -> None:
        """Test that parser failure raises FileParsingError."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".pdf"
        mock_path_class.return_value = mock_path

        mock_extractor = Mock(spec=ResumeExtractor)
        mock_create_extractor.return_value = mock_extractor
        
        pdf_parser = Mock(spec=FileParser)
        pdf_parser.parse.side_effect = Exception("Parser failed")

        framework = ResumeParserFramework(pdf_parser=pdf_parser)

        # Act & Assert
        with pytest.raises(FileParsingError, match="Failed to parse resume file"):
            framework.parse_resume("/path/to/resume.pdf")

    @patch.object(ResumeParserFramework, "_create_extractor")
    @patch("framework.resume_parser_framework.Path")
    def test_extractor_failure_propagates_error(self, mock_path_class: Mock, mock_create_extractor: Mock) -> None:
        """Test that extractor failure propagates the exception."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".pdf"
        mock_path_class.return_value = mock_path

        mock_extractor = Mock()
        mock_extractor.extract = Mock(side_effect=FieldExtractionError("Extraction failed"))
        mock_create_extractor.return_value = mock_extractor

        pdf_parser = Mock(spec=FileParser)
        pdf_parser.parse.return_value = "Resume text"

        framework = ResumeParserFramework(pdf_parser=pdf_parser)

        # Act & Assert
        with pytest.raises(FieldExtractionError, match="Extraction failed"):
            framework.parse_resume("/path/to/resume.pdf")


class TestResumeParserFrameworkUtilityMethods:
    """Test cases for utility methods."""

    @patch.object(ResumeParserFramework, "_create_extractor")
    def test_is_supported_file_with_pdf(self, mock_create_extractor: Mock) -> None:
        """Test is_supported_file with PDF extension."""
        # Arrange
        mock_extractor = Mock(spec=ResumeExtractor)
        mock_create_extractor.return_value = mock_extractor
        framework = ResumeParserFramework()

        # Act & Assert
        assert framework.is_supported_file("resume.pdf") is True
        assert framework.is_supported_file("resume.PDF") is True

    @patch.object(ResumeParserFramework, "_create_extractor")
    def test_is_supported_file_with_docx(self, mock_create_extractor: Mock) -> None:
        """Test is_supported_file with DOCX extension."""
        # Arrange
        mock_extractor = Mock(spec=ResumeExtractor)
        mock_create_extractor.return_value = mock_extractor
        framework = ResumeParserFramework()

        # Act & Assert
        assert framework.is_supported_file("resume.docx") is True
        assert framework.is_supported_file("resume.DOCX") is True

    @patch.object(ResumeParserFramework, "_create_extractor")
    def test_is_supported_file_with_doc(self, mock_create_extractor: Mock) -> None:
        """Test is_supported_file with DOC extension."""
        # Arrange
        mock_extractor = Mock(spec=ResumeExtractor)
        mock_create_extractor.return_value = mock_extractor
        framework = ResumeParserFramework()

        # Act & Assert
        assert framework.is_supported_file("resume.doc") is True

    @patch.object(ResumeParserFramework, "_create_extractor")
    def test_is_supported_file_with_unsupported_extension(self, mock_create_extractor: Mock) -> None:
        """Test is_supported_file with unsupported extension."""
        # Arrange
        mock_extractor = Mock(spec=ResumeExtractor)
        mock_create_extractor.return_value = mock_extractor
        framework = ResumeParserFramework()

        # Act & Assert
        assert framework.is_supported_file("resume.txt") is False
        assert framework.is_supported_file("resume.xlsx") is False
        assert framework.is_supported_file("resume") is False

    @patch.object(ResumeParserFramework, "_create_extractor")
    def test_get_supported_extensions(self, mock_create_extractor: Mock) -> None:
        """Test get_supported_extensions method."""
        # Arrange
        mock_extractor = Mock(spec=ResumeExtractor)
        mock_create_extractor.return_value = mock_extractor
        framework = ResumeParserFramework()

        # Act
        extensions = framework.get_supported_extensions()

        # Assert
        assert extensions == {".pdf", ".docx", ".doc"}
        assert isinstance(extensions, set)

    @patch.object(ResumeParserFramework, "_create_extractor")
    def test_get_supported_extensions_returns_copy(self, mock_create_extractor: Mock) -> None:
        """Test that get_supported_extensions returns a copy."""
        # Arrange
        mock_extractor = Mock(spec=ResumeExtractor)
        mock_create_extractor.return_value = mock_extractor
        framework = ResumeParserFramework()

        # Act
        extensions1 = framework.get_supported_extensions()
        extensions2 = framework.get_supported_extensions()

        # Modify one copy
        extensions1.add(".custom")

        # Assert - the second copy should not be affected
        assert ".custom" not in extensions2
        assert ".custom" not in framework.get_supported_extensions()
