"""Regex-based extraction strategy."""

import re
from typing import List

from interfaces import ExtractionStrategy, FieldSpec
from exceptions import InvalidStrategyConfigError, NoMatchFoundError


class RegexExtractionStrategy(ExtractionStrategy[List[str]]):
    """Extract fields using regular expression patterns."""

    def __init__(self, spec: FieldSpec):
        """Initialize with regex patterns.

        Args:
            spec: Field specification
            patterns: List of regex pattern strings to try in order

        Raises:
            InvalidStrategyConfigError: If patterns list is empty or invalid
        """
        self.spec = spec
        if not self.spec.regex_patterns:
            raise InvalidStrategyConfigError("At least one regex pattern must be provided")

        self.patterns: List[re.Pattern[str]] = []
        for pattern in self.spec.regex_patterns:
            try:
                self.patterns.append(re.compile(pattern, re.IGNORECASE | re.MULTILINE))
            except re.error as e:
                raise InvalidStrategyConfigError(
                    "Invalid regex pattern", original_exception=e
                ) from e

    def extract(self, text: str) -> List[str]:
        """Extract field using regex patterns.

        Tries each pattern in order and returns the first k matches for first regex that gets matches.

        Args:
            text: Text to extract from

        Returns:
            Extracted value (str for single-valued, List[str] for multi-valued)

        Raises:
            NoMatchFoundError: If no pattern matches
        """
        if not text or not text.strip():
            raise NoMatchFoundError("Cannot extract from empty text")

        for pattern in self.patterns:
            matches = pattern.findall(text)
            if matches:
                # Flatten matches if they are tuples (from groups) and remove falsey values
                if matches and isinstance(matches[0], tuple):
                    matches = [m for match in matches for m in match if m]

                if self.spec.top_k is not None:
                    # Multi-valued field
                    return (
                        matches[: self.spec.top_k] if self.spec.top_k > 0 else matches
                    )
                else:
                    # Single-valued field - return first match
                    return [matches[0]] if matches else []

        raise NoMatchFoundError(
            f"No matches found for field '{self.spec.field_type.value}' using {len(self.patterns)} patterns"
        )
