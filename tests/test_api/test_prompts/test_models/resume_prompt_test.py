"""
Unit tests for ResumePrompt model.
"""

import pytest
from datetime import datetime
from typing import Any
from pydantic import ValidationError

from api.prompts.models.resume_prompt import ResumePrompt, PersonaType


def test_resume_prompt_creation_valid(resume_prompt_data: dict) -> None:
    """Test creating a ResumePrompt with valid data."""
    prompt = ResumePrompt(**resume_prompt_data)
    
    assert prompt.name == resume_prompt_data["name"]
    assert prompt.description == resume_prompt_data["description"]
    assert prompt.prompt_template == resume_prompt_data["prompt_template"]
    assert prompt.variables == resume_prompt_data["variables"]
    assert prompt.persona_type == resume_prompt_data["persona_type"]
    assert prompt.version == resume_prompt_data["version"]
    assert prompt.is_active == resume_prompt_data["is_active"]
    assert isinstance(prompt.created_at, datetime)
    assert isinstance(prompt.updated_at, datetime)


def test_resume_prompt_model_validate(resume_prompt_data: dict) -> None:
    """Test creating ResumePrompt using model_validate."""
    prompt = ResumePrompt.model_validate(resume_prompt_data)
    
    assert prompt.name == resume_prompt_data["name"]
    assert prompt.persona_type == resume_prompt_data["persona_type"]


def test_resume_prompt_defaults() -> None:
    """Test ResumePrompt with minimal required fields."""
    prompt = ResumePrompt(
        name="minimal_prompt",
        prompt_template="Simple persona template",
        persona_type="basic"
    )
    
    assert prompt.name == "minimal_prompt"
    assert prompt.description is None
    assert prompt.variables == []
    assert prompt.version == 1
    assert prompt.is_active is True
    assert isinstance(prompt.created_at, datetime)
    assert isinstance(prompt.updated_at, datetime)
