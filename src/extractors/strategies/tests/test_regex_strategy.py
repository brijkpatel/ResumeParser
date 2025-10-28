"""Unit tests for RegexExtractionStrategy."""

import pytest

from interfaces import FieldSpec, FieldType
from extractors.strategies import RegexExtractionStrategy
from exceptions import InvalidStrategyConfigError, NoMatchFoundError


class TestRegexExtractionStrategy:
    """Tests for RegexExtractionStrategy."""

    def test_init_with_valid_patterns(self):
        """Test initialization with valid patterns."""
        spec = FieldSpec(field_type=FieldType.NAME)
        strategy = RegexExtractionStrategy(spec, [r"\d+", r"[a-z]+"])
        assert len(strategy.patterns) == 2

    def test_init_with_empty_patterns(self):
        """Test initialization with empty pattern list raises error."""
        spec = FieldSpec(field_type=FieldType.NAME)
        with pytest.raises(
            InvalidStrategyConfigError, match="At least one regex pattern"
        ):
            RegexExtractionStrategy(spec, [])

    def test_init_with_invalid_pattern(self):
        """Test initialization with invalid regex raises error."""
        spec = FieldSpec(field_type=FieldType.NAME)
        with pytest.raises(InvalidStrategyConfigError):
            RegexExtractionStrategy(spec, [r"(?P<unclosed"])

    def test_extract_single_value_first_match(self):
        """Test extracting single value returns first match."""
        spec = FieldSpec(field_type=FieldType.NAME)
        strategy = RegexExtractionStrategy(spec, [r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"])

        text = "Hello, I'm John Doe and this is Jane Smith."
        result = strategy.extract(text)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == "John Doe"

    def test_extract_multi_value_with_top_k(self):
        """Test extracting multiple values with top_k limit."""
        spec = FieldSpec(field_type=FieldType.SKILLS, top_k=3)
        strategy = RegexExtractionStrategy(spec, [r"\b[A-Z][a-z]+\b"])

        text = "Python Java JavaScript Ruby Go Rust"
        result = strategy.extract(text)

        assert isinstance(result, list)
        assert len(result) == 3
        assert result == ["Python", "Java", "JavaScript"]

    def test_extract_multi_value_no_limit(self):
        """Test extracting all matches when top_k is 0."""
        spec = FieldSpec(field_type=FieldType.SKILLS, top_k=0)
        strategy = RegexExtractionStrategy(spec, [r"\b\d+\b"])

        text = "Years: 2020, 2021, 2022, 2023"
        result = strategy.extract(text)

        assert len(result) == 4

    def test_extract_with_multiple_patterns_fallback(self):
        """Test that second pattern is tried if first fails."""
        spec = FieldSpec(field_type=FieldType.EMAIL)
        strategy = RegexExtractionStrategy(
            spec,
            [
                r"Email: ([\w\.-]+@[\w\.-]+\.\w+)",  # Labeled format
                r"\b[\w\.-]+@[\w\.-]+\.\w+\b",  # Generic email
            ],
        )

        text = "Contact: john@example.com"
        result = strategy.extract(text)

        assert result == ["john@example.com"]

    def test_extract_empty_text_raises_error(self):
        """Test extracting from empty text raises error."""
        spec = FieldSpec(field_type=FieldType.NAME)
        strategy = RegexExtractionStrategy(spec, [r"\w+"])

        with pytest.raises(NoMatchFoundError, match="Cannot extract from empty text"):
            strategy.extract("   ")

    def test_extract_no_match_raises_error(self):
        """Test no match raises NoMatchFoundError."""
        spec = FieldSpec(field_type=FieldType.EMAIL)
        strategy = RegexExtractionStrategy(spec, [r"\d{10}"])  # Phone number pattern

        with pytest.raises(NoMatchFoundError, match="No matches found"):
            strategy.extract("No numbers here!")

    def test_extract_with_groups_flattens_tuples(self):
        """Test that capture groups are properly flattened."""
        spec = FieldSpec(field_type=FieldType.EMAIL, top_k=0)
        strategy = RegexExtractionStrategy(spec, [r"(\w+)@(\w+)\.(\w+)"])

        text = "test@example.com"
        result = strategy.extract(text)

        assert isinstance(result, list)
        assert "test" in result
        assert "example" in result
