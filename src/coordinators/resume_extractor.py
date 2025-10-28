"""Coordinator class for orchestrating field extraction from resume text."""

from typing import Dict, List, Any, Optional
from interfaces import FieldExtractor, FieldType
from models import ResumeData
from utils import logger


class ResumeExtractor:
    """Orchestrates extraction of multiple fields from resume text.

    This coordinator class takes a dictionary of field extractors (with fallback
    strategies) and orchestrates the extraction process for all fields. It tries
    extractors in order until one succeeds, allowing for graceful degradation.

    Design Pattern: Coordinator/Orchestrator pattern with Chain of Responsibility
    - Coordinates multiple extractors (Strategy pattern instances)
    - Tries extractors in order until success
    - Handles the workflow of extracting all fields
    - Aggregates results into a single data structure
    - Allows fields to be None if all extraction attempts fail

    Attributes:
        extractors: Dictionary mapping field types to ordered list of extractors
    """

    def __init__(
        self,
        extractors: Dict[FieldType, List[FieldExtractor[Any]]],
    ):
        """Initialize the ResumeExtractor with field extractors.

        Args:
            extractors: Dictionary mapping field types to list of extractors.
                       Extractors are tried in order until one succeeds.

        Raises:
            ValueError: If extractors dict is None or empty
        """
        if not extractors:
            raise ValueError("extractors dictionary cannot be None or empty")

        # Validate all required field types are present
        required_fields = {FieldType.NAME, FieldType.EMAIL, FieldType.SKILLS}
        provided_fields = set(extractors.keys())

        if not required_fields.issubset(provided_fields):
            missing = required_fields - provided_fields
            raise ValueError(
                f"Missing required field types: {[f.value for f in missing]}"
            )

        self.extractors: Dict[FieldType, List[FieldExtractor[Any]]] = extractors

        logger.info(
            f"ResumeExtractor initialized with extractors for "
            f"{len(extractors)} field types"
        )

    def extract(self, text: str) -> ResumeData:
        """Extract all fields from the resume text and create ResumeData.

        This method orchestrates the extraction of all three fields (name, email,
        skills) from the provided text. For each field, it tries extractors in order
        until one succeeds. If all extractors fail for a field, that field will be
        None or empty in the result.

        Args:
            text: The resume text to extract fields from

        Returns:
            ResumeData object containing extracted fields (may have None values)

        Raises:
            ValueError: If the text is empty or invalid
        """
        if not text or not text.strip():
            raise ValueError("Resume text cannot be empty")

        logger.info("Starting field extraction from resume text")

        # Extract each field using the chain of extractors
        name = self._extract_field(FieldType.NAME, text)
        email = self._extract_field(FieldType.EMAIL, text)
        skills = self._extract_field(FieldType.SKILLS, text)

        # Create and return ResumeData object (fields can be None)
        resume_data = ResumeData(name=name, email=email, skills=skills)
        logger.info("Successfully created ResumeData object")
        return resume_data

    def _extract_field(self, field_type: FieldType, text: str) -> Optional[Any]:
        """Extract a single field using the chain of extractors.

        Tries each extractor for the field in order until one succeeds.
        If all fail, returns None (or empty list for skills).

        Args:
            field_type: The type of field to extract
            text: The text to extract from

        Returns:
            Extracted value or None if all extractors fail
        """
        extractors = self.extractors.get(field_type, [])
        field_name = field_type.value

        logger.debug(
            f"Attempting to extract '{field_name}' using {len(extractors)} extractor(s)"
        )

        for idx, extractor in enumerate(extractors, 1):
            try:
                logger.debug(
                    f"Trying extractor {idx}/{len(extractors)} for '{field_name}'"
                )
                result = extractor.extract(text)

                # Check if we got a meaningful result
                if result is not None and result != [] and result != "":
                    logger.info(
                        f"Successfully extracted '{field_name}' using {extractor.__class__.__name__}"
                    )
                    return result
                else:
                    logger.warning(
                        f"Extractor {idx} returned empty result for '{field_name}'"
                    )
            except Exception as e:
                logger.error(
                    f"Extractor {idx} failed for '{field_name}': {type(e).__name__}: {e}"
                )
                # Continue to next extractor
                continue

        # All extractors failed
        logger.error(
            f"All {len(extractors)} extractor(s) failed for '{field_name}'. "
            f"Returning None/empty."
        )

        # Return appropriate default based on field type
        if field_type == FieldType.SKILLS:
            return []  # Empty list for skills
        else:
            return None  # None for name/email
