"""Abstract base class for field extractors."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar("T")  # Generic type for extraction result


class FieldExtractor(ABC, Generic[T]):
    """Abstract base class for field extractors.

    This interface defines the contract for extracting specific fields from text.
    Concrete implementations should handle different extraction strategies like
    regex, NER, ML models, etc.

    Type parameter T represents the type of the extracted field:
    - str for name and email
    - List[str] for skills
    """

    @abstractmethod
    def extract(self, text: str) -> T:
        """Extract a specific field from the given text.

        Args:
            text: Text content to extract field from

        Returns:
            Extracted field value of type T

        Raises:
            FieldExtractionError: If extraction fails
        """
