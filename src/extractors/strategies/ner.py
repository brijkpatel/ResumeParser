"""NER-based extraction strategy using GLiNER."""

from typing import List, Optional
from gliner import GLiNER

from interfaces import ExtractionStrategy, FieldSpec
from exceptions import InvalidStrategyConfigError, NoMatchFoundError, StrategyExtractionError


class NERExtractionStrategy(ExtractionStrategy[List[str]]):
    """Extract fields using Named Entity Recognition (GLiNER)."""

    def __init__(
        self, 
        model_name: str = "urchade/gliner_multi_pii-v1", 
        default_entity_labels: Optional[List[str]] = None
    ):
        """Initialize NER strategy with GLiNER model.
        
        Args:
            model_name: GLiNER model to load (default: urchade/gliner_multi_pii-v1)
            default_entity_labels: Default entity labels if not in spec (e.g., ["person", "organization"])
            
        Raises:
            InvalidStrategyConfigError: If model cannot be loaded
        """
        try:
            self.model = GLiNER.from_pretrained(model_name)
        except Exception as e:
            raise InvalidStrategyConfigError(
                "Failed to load GLiNER model", 
                original_exception=e
            ) from e
        
        self.default_entity_labels = default_entity_labels

    def extract(self, text: str, spec: FieldSpec) -> List[str]:
        """Extract field using NER.
        
        Args:
            text: Text to extract from
            spec: Field specification with entity_label
            
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
        if spec.entity_label:
            entity_labels = [spec.entity_label]
        elif self.default_entity_labels:
            entity_labels = self.default_entity_labels
        
        if not entity_labels:
            raise InvalidStrategyConfigError(
                "entity_label must be provided in FieldSpec or as default_entity_labels"
            )

        try:
            # GLiNER predict_entities returns a list of entity dictionaries
            entities = self.model.predict_entities(text, entity_labels)
        except Exception as e:
            raise StrategyExtractionError(
                "GLiNER processing failed", 
                original_exception=e
            ) from e

        # Extract text from entity dictionaries
        entity_texts: List[str] = [ent["text"] for ent in entities]

        if not entity_texts:
            labels_str = ", ".join(entity_labels)
            raise NoMatchFoundError(
                f"No entities found with labels '{labels_str}' for field '{spec.field_type.value}'"
            )

        if spec.top_k is not None:
            # Multi-valued field
            return entity_texts[:spec.top_k] if spec.top_k > 0 else entity_texts
        else:
            # Single-valued field - return first entity
            return [entity_texts[0]]
