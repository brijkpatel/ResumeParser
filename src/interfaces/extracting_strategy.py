"""Defines the interface for extraction strategies used in field extraction."""

from dataclasses import dataclass
from typing import Optional, Generic, TypeVar, List
from abc import ABC, abstractmethod
from enum import Enum

T = TypeVar('T')

class FieldType(Enum):
    """Enumeration of supported field types for extraction."""
    NAME = "name"
    EMAIL = "email"
    SKILLS = "skills"

class StrategyType(Enum):
    """
    Enumeration of possible extraction strategy types.
    """
    REGEX = "regex"
    NER = "ner"
    LLM = "llm"

@dataclass(frozen=True)
class FieldSpec:
    """Minimal, immutable spec telling a strategy what to extract."""
    field_type: FieldType
    # Optional knobs for strategies (e.g., NER entity label, top-k for lists)
    regex_patterns: Optional[List[str]] = None  # e.g., for regex strategies
    entity_label: Optional[str] = None   # e.g., "PERSON" for NER
    top_k: Optional[int] = None          # e.g., for multi-valued fields like skills

class ExtractionStrategy(ABC, Generic[T]):
    """Strategy interface implemented by Regex/NER/LLM/etc."""
    @abstractmethod
    def extract(self, text: str, spec: FieldSpec) -> T:
        """Run the algorithm using the provided specification."""
        raise NotImplementedError