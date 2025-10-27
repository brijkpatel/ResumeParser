"""Interfaces for extraction strategies and specifications."""

from enum import Enum

class StrategyType(Enum):
    """
    Enumeration of possible extraction strategy types.
    """
    REGEX = "regex"
    NER = "ner"
    LLM = "llm"
