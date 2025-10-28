"""NER-based extraction strategy using GLiNER."""

from typing import List, Optional
from gliner import GLiNER  # type: ignore

from interfaces import ExtractionStrategy, FieldSpec
from exceptions import (
    InvalidStrategyConfigError,
    NoMatchFoundError,
    StrategyExtractionError,
)


class NERExtractionStrategy(ExtractionStrategy[List[str]]):
    """Extract fields using Named Entity Recognition (GLiNER)."""

    def __init__(
        self,
        spec: FieldSpec,
        model_name: str = "urchade/gliner_multi_pii-v1",
        default_entity_label: Optional[str] = None,
    ):
        """Initialize NER strategy with GLiNER model.

        Args:
            spec: Field specification
            model_name: GLiNER model to load (default: urchade/gliner_multi_pii-v1)
            default_entity_label: Default entity label if not in spec (e.g., "person", "organization")

        Raises:
            InvalidStrategyConfigError: If model cannot be loaded
        """
        self.spec = spec
        self.default_entity_label = default_entity_label
        try:
            self.model = GLiNER.from_pretrained(model_name)  # type: ignore
        except Exception as e:
            raise InvalidStrategyConfigError(
                "Failed to load GLiNER model", original_exception=e
            ) from e

    def extract(self, text: str) -> List[str]:
        """Extract field using NER.

        Args:
            text: Text to extract from

        Returns:
            Extracted entity/entities

        Raises:
            NoMatchFoundError: If no entities found
            InvalidStrategyConfigError: If entity_label not provided
        """
        if not text or not text.strip():
            raise NoMatchFoundError("Cannot extract from empty text")

        # GLiNER expects a list of labels to search for
        entity_labels = None
        if self.spec.entity_label:
            entity_labels = [self.spec.entity_label]
        elif self.default_entity_label:
            entity_labels = [self.default_entity_label]

        if not entity_labels:
            raise InvalidStrategyConfigError(
                "entity_label must be provided in FieldSpec or as default_entity_label"
            )

        try:
            # GLiNER predict_entities returns a list of entity dictionaries
            entities = self.model.predict_entities(text, entity_labels)  # type: ignore
        except Exception as e:
            raise StrategyExtractionError(
                "GLiNER processing failed", original_exception=e
            ) from e

        # Extract text from entity dictionaries
        entity_texts: List[str] = [ent["text"] for ent in entities]  # type: ignore

        if not entity_texts:
            raise NoMatchFoundError("No entities found")

        if self.spec.top_k is not None:
            # Multi-valued field
            return (
                entity_texts[: self.spec.top_k] if self.spec.top_k > 0 else entity_texts
            )
        else:
            # Single-valued field - return first entity
            return [entity_texts[0]]
