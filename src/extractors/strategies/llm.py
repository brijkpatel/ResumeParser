"""LLM-based extraction strategy using Google Gemini."""

import json
from typing import List
import google.generativeai as genai  # type: ignore

from interfaces import ExtractionStrategy, FieldSpec, FieldType
from exceptions import (
    InvalidStrategyConfigError,
    NoMatchFoundError,
    ExternalServiceError,
)


class LLMExtractionStrategy(ExtractionStrategy[List[str]]):
    """Extract fields using Google Gemini LLM."""

    def __init__(self, spec: FieldSpec, model_name: str = "gemini-2.0-flash-exp"):
        """Initialize LLM strategy with Gemini.

        Args:
            spec: Field specification
            model_name: Gemini model name (default: gemini-2.0-flash-exp which requires no API key)

        Raises:
            InvalidStrategyConfigError: If model initialization fails
        """
        self.spec = spec
        try:
            self.model = genai.GenerativeModel(model_name)  # type: ignore
        except Exception as e:
            raise InvalidStrategyConfigError(
                "Failed to initialize Gemini model", original_exception=e
            ) from e

    def extract(self, text: str) -> List[str]:
        """Extract field using LLM.

        Args:
            text: Text to extract from

        Returns:
            Extracted value(s) as list

        Raises:
            NoMatchFoundError: If LLM cannot extract the field
            ExternalServiceError: If API call fails
        """
        if not text or not text.strip():
            raise NoMatchFoundError("Cannot extract from empty text")

        prompt = self._build_prompt(text, self.spec)

        try:
            response = self.model.generate_content(prompt)  # type: ignore
            if not response or not response.text:
                raise NoMatchFoundError("LLM returned empty response for field")

            result = self._parse_response(response.text, self.spec)
            return result

        except NoMatchFoundError as e:
            raise e
        except Exception as e:
            raise ExternalServiceError(
                "Gemini API call failed", original_exception=e
            ) from e

    def _build_prompt(self, text: str, spec: FieldSpec) -> str:
        """Build prompt for LLM based on field type."""
        field_instructions = {
            FieldType.NAME: "Extract the person's full name from the resume text.",
            FieldType.EMAIL: "Extract the person's email address from the resume text.",
            FieldType.SKILLS: "Extract all technical skills mentioned in the resume text as a JSON array.",
        }

        instruction = field_instructions.get(spec.field_type)

        prompt = f"""{instruction}
            Return the result as a valid JSON array of strings.
            If nothing is found, return an empty array: []

            Text:
            {text}
            Response (JSON array only):"""

        return prompt

    def _parse_response(self, response_text: str, spec: FieldSpec) -> List[str]:
        """Parse LLM response based on field type."""
        response_text = response_text.strip()

        if spec.top_k is not None:
            # Multi-valued field - expect JSON array
            try:
                # Try to extract JSON array from response
                if "[" in response_text and "]" in response_text:
                    start = response_text.index("[")
                    end = response_text.rindex("]") + 1
                    json_str = response_text[start:end]
                    result = json.loads(json_str)

                    if not isinstance(result, list):
                        raise ValueError("Response is not a list")

                    # Filter and limit results
                    result = [str(item).strip() for item in result if item]  # type: ignore
                    if spec.top_k > 0:
                        result = result[: spec.top_k]

                    if not result:
                        raise NoMatchFoundError(
                            f"LLM found no values for field '{spec.field_type.value}'"
                        )

                    return result
                else:
                    raise ValueError("No JSON array found in response")

            except (json.JSONDecodeError, ValueError) as e:
                raise ExternalServiceError(
                    "Failed to parse LLM response as JSON", original_exception=e
                ) from e
        else:
            # Single-valued field - return as single-item list
            if response_text.upper() == "NOT_FOUND" or not response_text:
                raise NoMatchFoundError(
                    f"LLM could not find field '{spec.field_type.value}'"
                )

            return [response_text]
