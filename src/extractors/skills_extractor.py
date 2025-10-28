"""Email extraction implementations using different strategies."""

from typing import List

from interfaces import FieldExtractor, ExtractionStrategy
from exceptions import FieldExtractionError


class SkillsExtractor(FieldExtractor[List[str]]):
    """Extract Skills from provided text"""

    def __init__(self, extraction_strategy: ExtractionStrategy[List[str]]):
        """Initialize the regex skills extractor."""
        self.extraction_strategy = extraction_strategy

    def extract(self, text: str) -> List[str]:
        """Extract skills using regex patterns.

        Args:
            text: Text content to extract skills from

        Returns:
            List of extracted skills

        Raises:
            FieldExtractionError: If skills extraction fails
        """
        processed_text = self.validate_input(text)

        try:
            skills = self.extraction_strategy.extract(processed_text)
            if not skills:
                raise FieldExtractionError("No skills found")
            return skills
        except Exception as e:
            raise FieldExtractionError(
                "Skills extraction failed", original_exception=e
            ) from e

    def validate_input(self, text: str) -> str:
        """Validate and preprocess the input text.

        Strips whitespace and ensures the text has at least 5 characters.

        Args:
            text: The input text to validate

        Returns:
            The stripped text

        Raises:
            FieldExtractionError: If validation fails
        """
        text = text.strip()
        if len(text) < 2:
            raise FieldExtractionError(
                "Input text must be at least 2 characters long after stripping"
            )
        return text
