"""Email extraction implementations using different strategies."""

import re
from typing import List

from interfaces import FieldExtractor, ExtractionStrategy
from exceptions import FieldExtractionError
from utils import logger


class EmailExtractor(FieldExtractor[str]):
    """Extract email address from provided text"""

    def __init__(self, extraction_strategy: ExtractionStrategy[List[str]]):
        """Initialize the email extractor."""
        self.extraction_strategy = extraction_strategy

    def extract(self, text: str) -> str:
        """Extract email.

        Args:
            text: Text content to extract email from
        Returns:
            Extracted email address

        Raises:
            FieldExtractionError: If email extraction fails
        """
        processed_text = self.validate_input(text)

        try:
            emails = self.extraction_strategy.extract(processed_text)
            if not emails:
                raise FieldExtractionError("No email addresses found")
            email = emails[0]
            logger.debug(f"Extracted email: {email}")
            self.validate_email_format(email)
            return email
        except Exception as e:
            raise FieldExtractionError(
                "Email extraction failed", original_exception=e
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
        if len(text) < 5:
            raise FieldExtractionError(
                "Input text must be at least 5 characters long after stripping"
            )
        return text

    # Might be hard to for other classes but email format is easy to validate
    def validate_email_format(self, email: str) -> None:
        """Validate email format using regex.

        Args:
            email: The email address to validate

        Raises:
            FieldExtractionError: If email format is invalid
        """
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise FieldExtractionError(f"Invalid email format")
