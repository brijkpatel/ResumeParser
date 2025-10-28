"""Email extraction implementations using different strategies."""

import re
from typing import List

from interfaces import FieldExtractor, StrategyType, ExtractionStrategy
from exceptions import FieldExtractionError
from utils import logger


class EmailExtractor(FieldExtractor[str]):
    """Extract email addresses from provided text"""

    def __init__(self,extraction_strategy: ExtractionStrategy[List[str]]):
        """Initialize the regex email extractor."""
        self.extraction_strategy = extraction_strategy

    def extract(self, text: str) -> str:
        """Extract email using regex patterns.

        Args:
            text: Text content to extract email from
        Returns:
            Extracted email address

        Raises:
            FieldExtractionError: If email extraction fails
        """
        processed_text = self.validate_input(text)

        
        for strategy in preferred_strategies:
            if strategy == StrategyType.REGEX:

        # Comprehensive email regex pattern
        email_pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"

        # Find all email matches
        email_matches = re.findall(email_pattern, processed_text, re.IGNORECASE)

        if not email_matches:
            raise FieldExtractionError("Could not extract email from text")

        # Filter and validate emails
        valid_emails = []
        for email in email_matches:
            if self._is_valid_email(email):
                valid_emails.append(email.lower())

        if not valid_emails:
            raise FieldExtractionError("No valid email addresses found")

        # Remove duplicates while preserving order
        unique_emails = list(dict.fromkeys(valid_emails))

        # Choose the best email (prioritize personal emails over generic ones)
        best_email = self._choose_best_email(unique_emails)

        logger.info(f"Extracted email: {best_email}")
        return best_email

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
