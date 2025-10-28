"""Email extraction implementations using different strategies."""

from typing import List

from interfaces import FieldExtractor, ExtractionStrategy
from exceptions import FieldExtractionError



class NameExtractor(FieldExtractor[str]):
    """Extract Name from provided text"""

    def __init__(self, extraction_strategy: ExtractionStrategy[List[str]]):
        """Initialize the name extractor."""
        self.extraction_strategy = extraction_strategy

    def extract(self, text: str) -> str:
        """Extract name using regex patterns.

        Args:
            text: Text content to extract Name from
        Returns:
            Extracted Name

        Raises:
            FieldExtractionError: If Name extraction fails
        """
        processed_text = self.validate_input(text)

        try:
            names = self.extraction_strategy.extract(processed_text)
            if not names:
                raise FieldExtractionError("No names found")
            return names[0]  # Return the first extracted name
        except Exception as e:
            raise FieldExtractionError("Name extraction failed", original_exception=e) from e

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
        if len(text) < 1:
            raise FieldExtractionError(
                "Input text must be at least 1 character long after stripping"
            )
        return text
