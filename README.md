# ResumeParser

A Python-based resume parsing framework that extracts structured information from resumes in various formats.

## Features

- **Multi-Strategy Extraction**: Each field (name, email, skills) can use multiple extraction strategies with automatic fallback
- **Config-Driven**: Define preferred strategy order per field type via configuration
- **Graceful Degradation**: Continues extraction even when individual strategies fail, with comprehensive error logging
- **Multiple File Formats**: Supports PDF and DOCX resume formats
- **Extensible Design**: Easy to add new extraction strategies and field types

## Architecture

The framework follows a layered architecture with multiple design patterns:

- **Facade Pattern**: `ResumeParserFramework` provides simple interface for resume parsing
- **Coordinator Pattern**: `ResumeExtractor` orchestrates field extraction across multiple extractors
- **Factory Pattern**: `create_extractor()` creates appropriate extractor+strategy combinations
- **Strategy Pattern**: Multiple extraction strategies (Regex, NER, LLM) for each field type
- **Chain of Responsibility**: Tries strategies in order until successful extraction

## Quick Start

```python
from framework import ResumeParserFramework

# Use default configuration
framework = ResumeParserFramework()
resume_data = framework.parse_resume("path/to/resume.pdf")

print(f"Name: {resume_data.name}")
print(f"Email: {resume_data.email}")
print(f"Skills: {resume_data.skills}")
```

## Custom Configuration

```python
from framework import ResumeParserFramework
from config import ExtractionConfig
from interfaces import FieldType, StrategyType

# Define custom strategy preferences
custom_config = ExtractionConfig(
    strategy_preferences={
        FieldType.NAME: [StrategyType.LLM, StrategyType.NER],
        FieldType.EMAIL: [StrategyType.REGEX, StrategyType.LLM],
        FieldType.SKILLS: [StrategyType.LLM, StrategyType.NER],
    }
)

framework = ResumeParserFramework(config=custom_config)
resume_data = framework.parse_resume("path/to/resume.docx")
```

## Default Configuration

By default, the framework uses the following strategy priorities:

- **NAME**: NER → LLM
- **EMAIL**: REGEX → NER → LLM  
- **SKILLS**: LLM → NER

This balances accuracy and performance, starting with faster methods and falling back to more sophisticated approaches as needed.

## Installation

```bash
pip install -r requirements.txt
```

## Running Tests

```bash
pytest
```