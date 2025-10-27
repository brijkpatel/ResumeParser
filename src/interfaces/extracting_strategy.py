"""This module is only as alternate solution. Not currently used. Keeping here for reference during assessment.
Concrete strategies can be defined based on field specs and let factory handle the instantiation for field + strategy combinations.
Since strategies are reusable with different field specs, this can reduce number of classes.
For e.g. Pass different Regex for regex strategy, Entity label for NER strategy, etc., LLM prompt can be generalized and only need field names replaced.
"""

from dataclasses import dataclass
from typing import Optional, Generic, TypeVar
from abc import ABC, abstractmethod
from enum import Enum

T = TypeVar('T')

class FieldType(Enum):
    NAME = "name"
    EMAIL = "email"
    SKILLS = "skills"

@dataclass(frozen=True)
class FieldSpec:
    """Minimal, immutable spec telling a strategy what to extract."""
    field_type: FieldType
    # Optional knobs for strategies (e.g., NER entity label, top-k for lists)
    entity_label: Optional[str] = None   # e.g., "PERSON" for NER
    top_k: Optional[int] = None          # e.g., for multi-valued fields like skills

class ExtractionStrategy(ABC, Generic[T]):
    """Strategy interface implemented by Regex/NER/LLM/etc."""
    @abstractmethod
    def extract(self, text: str, spec: FieldSpec) -> T:
        """Run the algorithm using the provided specification."""
        raise NotImplementedError