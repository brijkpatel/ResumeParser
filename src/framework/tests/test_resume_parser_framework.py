"""Tests for ResumeParserFramework."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from framework.resume_parser_framework import ResumeParserFramework
from coordinators import ResumeExtractor
from interfaces import FileParser
from models import ResumeData
from exceptions import (
    UnsupportedFileFormatError,
    FileParsingError,
    FieldExtractionError,
)


class TestResumeParserFrameworkInitialization:
    """Test cases for ResumeParserFramework initialization."""

    def test_initialization_with_extractor(self):
        """Test successful initialization with extractor."""
        # Arrange
        extractor = Mock(spec=ResumeExtractor)

        # Act
        framework = ResumeParserFramework(extractor)

        # Assert
        assert framework.extractor == extractor
        assert len(framework.parsers) == 3
        assert ".pdf" in framework.parsers
        assert ".docx" in framework.parsers
        assert ".doc" in framework.parsers

    def test_initialization_with_custom_parsers(self):
        """Test initialization with custom parsers."""
        # Arrange
        extractor = Mock(spec=ResumeExtractor)
        pdf_parser = Mock(spec=FileParser)
        word_parser = Mock(spec=FileParser)

        # Act
        framework = ResumeParserFramework(extractor, pdf_parser, word_parser)

        # Assert
        assert framework.parsers[".pdf"] == pdf_parser
        assert framework.parsers[".docx"] == word_parser
        assert framework.parsers[".doc"] == word_parser

    def test_initialization_with_none_extractor_raises_error(self):
        """Test that None extractor raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="ResumeExtractor cannot be None"):
            ResumeParserFramework(None)  # type: ignore


class TestResumeParserFrameworkParseResume:
    """Test cases for parse_resume method."""

    @patch("framework.resume_parser_framework.Path")
    def test_parse_pdf_resume_success(self, mock_path_class):
        """Test successful parsing of PDF resume."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".pdf"
        mock_path_class.return_value = mock_path

        extractor = Mock(spec=ResumeExtractor)
        resume_data = ResumeData(
            name="John Doe", email="john@example.com", skills=["Python"]
        )
        extractor.extract.return_value = resume_data

        pdf_parser = Mock(spec=FileParser)
        pdf_parser.parse.return_value = "Resume text content"

        framework = ResumeParserFramework(extractor, pdf_parser=pdf_parser)

        # Act
        result = framework.parse_resume("/path/to/resume.pdf")

        # Assert
        assert result == resume_data
        pdf_parser.parse.assert_called_once_with("/path/to/resume.pdf")
        extractor.extract.assert_called_once_with("Resume text content")

    @patch("framework.resume_parser_framework.Path")
    def test_parse_docx_resume_success(self, mock_path_class):
        """Test successful parsing of DOCX resume."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".docx"
        mock_path_class.return_value = mock_path

        extractor = Mock(spec=ResumeExtractor)
        resume_data = ResumeData(
            name="Jane Smith", email="jane@example.com", skills=["Java"]
        )
        extractor.extract.return_value = resume_data

        word_parser = Mock(spec=FileParser)
        word_parser.parse.return_value = "DOCX resume text"

        framework = ResumeParserFramework(extractor, word_parser=word_parser)

        # Act
        result = framework.parse_resume("/path/to/resume.docx")

        # Assert
        assert result == resume_data
        word_parser.parse.assert_called_once_with("/path/to/resume.docx")

    @patch("framework.resume_parser_framework.Path")
    def test_parse_doc_resume_success(self, mock_path_class):
        """Test successful parsing of DOC resume."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".doc"
        mock_path_class.return_value = mock_path

        extractor = Mock(spec=ResumeExtractor)
        resume_data = ResumeData(
            name="Bob Johnson", email="bob@example.com", skills=["SQL"]
        )
        extractor.extract.return_value = resume_data

        word_parser = Mock(spec=FileParser)
        word_parser.parse.return_value = "DOC resume text"

        framework = ResumeParserFramework(extractor, word_parser=word_parser)

        # Act
        result = framework.parse_resume("/path/to/resume.doc")

        # Assert
        assert result == resume_data
        word_parser.parse.assert_called_once_with("/path/to/resume.doc")

    @patch("framework.resume_parser_framework.Path")
    def test_parse_resume_with_uppercase_extension(self, mock_path_class):
        """Test parsing resume with uppercase file extension."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".PDF"
        mock_path_class.return_value = mock_path

        extractor = Mock(spec=ResumeExtractor)
        resume_data = ResumeData(
            name="Alice", email="alice@example.com", skills=["Python"]
        )
        extractor.extract.return_value = resume_data

        pdf_parser = Mock(spec=FileParser)
        pdf_parser.parse.return_value = "Resume text"

        framework = ResumeParserFramework(extractor, pdf_parser=pdf_parser)

        # Act
        result = framework.parse_resume("/path/to/RESUME.PDF")

        # Assert
        assert result == resume_data


class TestResumeParserFrameworkFileValidation:
    """Test cases for file validation."""

    @patch("framework.resume_parser_framework.Path")
    def test_parse_nonexistent_file_raises_error(self, mock_path_class):
        """Test that non-existent file raises FileNotFoundError."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = False
        mock_path_class.return_value = mock_path

        extractor = Mock(spec=ResumeExtractor)
        framework = ResumeParserFramework(extractor)

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Resume file not found"):
            framework.parse_resume("/path/to/nonexistent.pdf")

    @patch("framework.resume_parser_framework.Path")
    def test_parse_directory_raises_error(self, mock_path_class):
        """Test that directory path raises ValueError."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = False
        mock_path_class.return_value = mock_path

        extractor = Mock(spec=ResumeExtractor)
        framework = ResumeParserFramework(extractor)

        # Act & Assert
        with pytest.raises(ValueError, match="Path is not a file"):
            framework.parse_resume("/path/to/directory")

    @patch("framework.resume_parser_framework.Path")
    def test_parse_unsupported_extension_raises_error(self, mock_path_class):
        """Test that unsupported file extension raises UnsupportedFileFormatError."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".txt"
        mock_path_class.return_value = mock_path

        extractor = Mock(spec=ResumeExtractor)
        framework = ResumeParserFramework(extractor)

        # Act & Assert
        with pytest.raises(
            UnsupportedFileFormatError, match="Unsupported file format: .txt"
        ):
            framework.parse_resume("/path/to/resume.txt")

    @patch("framework.resume_parser_framework.Path")
    def test_parse_no_extension_raises_error(self, mock_path_class):
        """Test that file with no extension raises UnsupportedFileFormatError."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ""
        mock_path_class.return_value = mock_path

        extractor = Mock(spec=ResumeExtractor)
        framework = ResumeParserFramework(extractor)

        # Act & Assert
        with pytest.raises(UnsupportedFileFormatError):
            framework.parse_resume("/path/to/resume")


class TestResumeParserFrameworkErrorHandling:
    """Test cases for error handling."""

    @patch("framework.resume_parser_framework.Path")
    def test_parser_failure_raises_file_parsing_error(self, mock_path_class):
        """Test that parser failure raises FileParsingError."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".pdf"
        mock_path_class.return_value = mock_path

        extractor = Mock(spec=ResumeExtractor)
        pdf_parser = Mock(spec=FileParser)
        pdf_parser.parse.side_effect = Exception("Parser failed")

        framework = ResumeParserFramework(extractor, pdf_parser=pdf_parser)

        # Act & Assert
        with pytest.raises(FileParsingError, match="Failed to parse resume file"):
            framework.parse_resume("/path/to/resume.pdf")

    @patch("framework.resume_parser_framework.Path")
    def test_extractor_failure_propagates_error(self, mock_path_class):
        """Test that extractor failure propagates the exception."""
        # Arrange
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".pdf"
        mock_path_class.return_value = mock_path

        extractor = Mock(spec=ResumeExtractor)
        extractor.extract.side_effect = FieldExtractionError("Extraction failed")

        pdf_parser = Mock(spec=FileParser)
        pdf_parser.parse.return_value = "Resume text"

        framework = ResumeParserFramework(extractor, pdf_parser=pdf_parser)

        # Act & Assert
        with pytest.raises(FieldExtractionError, match="Extraction failed"):
            framework.parse_resume("/path/to/resume.pdf")


class TestResumeParserFrameworkUtilityMethods:
    """Test cases for utility methods."""

    def test_is_supported_file_with_pdf(self):
        """Test is_supported_file with PDF extension."""
        # Arrange
        extractor = Mock(spec=ResumeExtractor)
        framework = ResumeParserFramework(extractor)

        # Act & Assert
        assert framework.is_supported_file("resume.pdf") is True
        assert framework.is_supported_file("resume.PDF") is True

    def test_is_supported_file_with_docx(self):
        """Test is_supported_file with DOCX extension."""
        # Arrange
        extractor = Mock(spec=ResumeExtractor)
        framework = ResumeParserFramework(extractor)

        # Act & Assert
        assert framework.is_supported_file("resume.docx") is True
        assert framework.is_supported_file("resume.DOCX") is True

    def test_is_supported_file_with_doc(self):
        """Test is_supported_file with DOC extension."""
        # Arrange
        extractor = Mock(spec=ResumeExtractor)
        framework = ResumeParserFramework(extractor)

        # Act & Assert
        assert framework.is_supported_file("resume.doc") is True

    def test_is_supported_file_with_unsupported_extension(self):
        """Test is_supported_file with unsupported extension."""
        # Arrange
        extractor = Mock(spec=ResumeExtractor)
        framework = ResumeParserFramework(extractor)

        # Act & Assert
        assert framework.is_supported_file("resume.txt") is False
        assert framework.is_supported_file("resume.xlsx") is False
        assert framework.is_supported_file("resume") is False

    def test_get_supported_extensions(self):
        """Test get_supported_extensions method."""
        # Arrange
        extractor = Mock(spec=ResumeExtractor)
        framework = ResumeParserFramework(extractor)

        # Act
        extensions = framework.get_supported_extensions()

        # Assert
        assert extensions == {".pdf", ".docx", ".doc"}
        assert isinstance(extensions, set)

    def test_get_supported_extensions_returns_copy(self):
        """Test that get_supported_extensions returns a copy."""
        # Arrange
        extractor = Mock(spec=ResumeExtractor)
        framework = ResumeParserFramework(extractor)

        # Act
        extensions1 = framework.get_supported_extensions()
        extensions2 = framework.get_supported_extensions()

        # Modify one copy
        extensions1.add(".custom")

        # Assert - the second copy should not be affected
        assert ".custom" not in extensions2
        assert ".custom" not in framework.get_supported_extensions()
