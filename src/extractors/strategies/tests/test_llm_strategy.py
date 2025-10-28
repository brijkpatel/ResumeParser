"""Unit tests for LLMExtractionStrategy."""

import pytest
from unittest.mock import Mock, patch

from interfaces.extracting_strategy import FieldSpec, FieldType
from extractors.strategies.llm import LLMExtractionStrategy
from exceptions import (
    InvalidStrategyConfigError,
    NoMatchFoundError,
    ExternalServiceError,
)


class TestLLMExtractionStrategy:
    """Tests for LLMExtractionStrategy."""

    @patch('extractors.strategies.llm.genai.configure')
    @patch('extractors.strategies.llm.genai.GenerativeModel')
    def test_init_without_api_key(self, mock_model_class, mock_configure):
        """Test initialization without API key works for free model."""
        with patch.dict('os.environ', {}, clear=True):
            mock_model = Mock()
            mock_model_class.return_value = mock_model
            
            strategy = LLMExtractionStrategy()
            
            # Should not call configure without API key
            mock_configure.assert_not_called()
            assert strategy.model == mock_model

    @patch('extractors.strategies.llm.genai.configure')
    @patch('extractors.strategies.llm.genai.GenerativeModel')
    def test_init_with_api_key(self, mock_model_class, mock_configure):
        """Test successful initialization with API key."""
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        strategy = LLMExtractionStrategy(api_key="test_key")
        
        mock_configure.assert_called_once_with(api_key="test_key")
        assert strategy.model == mock_model

    @patch('extractors.strategies.llm.genai.configure')
    @patch('extractors.strategies.llm.genai.GenerativeModel')
    def test_init_model_failure(self, mock_model_class, mock_configure):
        """Test model initialization failure raises error."""
        mock_model_class.side_effect = Exception("Model init failed")
        
        with pytest.raises(InvalidStrategyConfigError):
            LLMExtractionStrategy(api_key="test_key")

    @patch('extractors.strategies.llm.genai.configure')
    @patch('extractors.strategies.llm.genai.GenerativeModel')
    def test_extract_single_value(self, mock_model_class, mock_configure):
        """Test extracting single value."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "John Doe"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        strategy = LLMExtractionStrategy(api_key="test_key")
        spec = FieldSpec(field_type=FieldType.NAME)
        
        result = strategy.extract("My name is John Doe", spec)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == "John Doe"

    @patch('extractors.strategies.llm.genai.configure')
    @patch('extractors.strategies.llm.genai.GenerativeModel')
    def test_extract_multi_value_json(self, mock_model_class, mock_configure):
        """Test extracting multiple values from JSON response."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '["Python", "Java", "JavaScript"]'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        strategy = LLMExtractionStrategy(api_key="test_key")
        spec = FieldSpec(field_type=FieldType.SKILLS, top_k=2)
        
        result = strategy.extract("Skills: Python, Java, JavaScript", spec)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result == ["Python", "Java"]

    @patch('extractors.strategies.llm.genai.configure')
    @patch('extractors.strategies.llm.genai.GenerativeModel')
    def test_extract_multi_value_with_extra_text(self, mock_model_class, mock_configure):
        """Test extracting JSON array embedded in response text."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = 'Here are the skills: ["Python", "Java"] from the text.'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        strategy = LLMExtractionStrategy(api_key="test_key")
        spec = FieldSpec(field_type=FieldType.SKILLS, top_k=0)
        
        result = strategy.extract("Some text", spec)
        
        assert result == ["Python", "Java"]

    @patch('extractors.strategies.llm.genai.configure')
    @patch('extractors.strategies.llm.genai.GenerativeModel')
    def test_extract_empty_text_raises_error(self, mock_model_class, mock_configure):
        """Test empty text raises error."""
        mock_model_class.return_value = Mock()
        
        strategy = LLMExtractionStrategy(api_key="test_key")
        spec = FieldSpec(field_type=FieldType.NAME)
        
        with pytest.raises(NoMatchFoundError, match="Cannot extract from empty text"):
            strategy.extract("   ", spec)

    @patch('extractors.strategies.llm.genai.configure')
    @patch('extractors.strategies.llm.genai.GenerativeModel')
    def test_extract_not_found_response(self, mock_model_class, mock_configure):
        """Test NOT_FOUND response raises error."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "NOT_FOUND"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        strategy = LLMExtractionStrategy(api_key="test_key")
        spec = FieldSpec(field_type=FieldType.NAME)
        
        with pytest.raises(NoMatchFoundError, match="LLM could not find field"):
            strategy.extract("Some text", spec)

    @patch('extractors.strategies.llm.genai.configure')
    @patch('extractors.strategies.llm.genai.GenerativeModel')
    def test_extract_empty_response(self, mock_model_class, mock_configure):
        """Test empty LLM response raises error."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = ""
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        strategy = LLMExtractionStrategy(api_key="test_key")
        spec = FieldSpec(field_type=FieldType.NAME)
        
        with pytest.raises(NoMatchFoundError, match="LLM returned empty response"):
            strategy.extract("Some text", spec)

    @patch('extractors.strategies.llm.genai.configure')
    @patch('extractors.strategies.llm.genai.GenerativeModel')
    def test_extract_invalid_json_raises_error(self, mock_model_class, mock_configure):
        """Test invalid JSON response raises error."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '["Python", "Java"'  # Invalid JSON
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        strategy = LLMExtractionStrategy(api_key="test_key")
        spec = FieldSpec(field_type=FieldType.SKILLS, top_k=0)
        
        with pytest.raises(ExternalServiceError):
            strategy.extract("Some text", spec)

    @patch('extractors.strategies.llm.genai.configure')
    @patch('extractors.strategies.llm.genai.GenerativeModel')
    def test_extract_api_failure(self, mock_model_class, mock_configure):
        """Test API failure raises ExternalServiceError."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model
        
        strategy = LLMExtractionStrategy(api_key="test_key")
        spec = FieldSpec(field_type=FieldType.NAME)
        
        with pytest.raises(ExternalServiceError):
            strategy.extract("Some text", spec)

    @patch('extractors.strategies.llm.genai.configure')
    @patch('extractors.strategies.llm.genai.GenerativeModel')
    def test_extract_empty_json_array(self, mock_model_class, mock_configure):
        """Test empty JSON array raises NoMatchFoundError."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '[]'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        strategy = LLMExtractionStrategy(api_key="test_key")
        spec = FieldSpec(field_type=FieldType.SKILLS, top_k=0)
        
        with pytest.raises(NoMatchFoundError, match="LLM found no values"):
            strategy.extract("Some text", spec)

    @patch('extractors.strategies.llm.genai.configure')
    @patch('extractors.strategies.llm.genai.GenerativeModel')
    def test_extract_non_list_json_response(self, mock_model_class, mock_configure):
        """Test non-list JSON response raises error."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '{"key": "value"}'  # Object instead of array
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        strategy = LLMExtractionStrategy(api_key="test_key")
        spec = FieldSpec(field_type=FieldType.SKILLS, top_k=0)
        
        with pytest.raises(ExternalServiceError):
            strategy.extract("Some text", spec)

    @patch('extractors.strategies.llm.genai.configure')
    @patch('extractors.strategies.llm.genai.GenerativeModel')
    def test_build_prompt_for_different_field_types(self, mock_model_class, mock_configure):
        """Test prompt building for different field types."""
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        strategy = LLMExtractionStrategy(api_key="test_key")
        
        # Test NAME field
        prompt_name = strategy._build_prompt("text", FieldSpec(field_type=FieldType.NAME))
        assert "full name" in prompt_name.lower()
        assert "NOT_FOUND" in prompt_name
        
        # Test SKILLS field with top_k
        prompt_skills = strategy._build_prompt("text", FieldSpec(field_type=FieldType.SKILLS, top_k=5))
        assert "skills" in prompt_skills.lower()
        assert "JSON array" in prompt_skills
