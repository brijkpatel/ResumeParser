"""Interfaces module for abstract base classes and protocols."""
from .file_parser import FileParser
from .field_extractor import FieldExtractor 
from .strategies import StrategyType
__all__ = [
    "FileParser",
    "FieldExtractor",
    "StrategyType",
]