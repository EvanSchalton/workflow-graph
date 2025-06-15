"""
Unit tests for TaskPrompt model.
"""

import pytest
from datetime import datetime
from typing import Any
from pydantic import ValidationError

from api.prompts.models.task_prompt import TaskPrompt


def test_task_prompt_creation_valid(task_prompt_data: dict) -> None:
    """Test creating a TaskPrompt with valid data."""
    prompt = TaskPrompt(**task_prompt_data)
    
    assert prompt.name == task_prompt_data["name"]
    assert prompt.description == task_prompt_data["description"]
    assert prompt.prompt_template == task_prompt_data["prompt_template"]
    assert prompt.variables == task_prompt_data["variables"]
    assert prompt.task_type == task_prompt_data["task_type"]
    assert prompt.version == task_prompt_data["version"]
    assert prompt.is_active == task_prompt_data["is_active"]
    assert isinstance(prompt.created_at, datetime)
    assert isinstance(prompt.updated_at, datetime)


def test_task_prompt_model_validate(task_prompt_data: dict) -> None:
    """Test creating TaskPrompt using model_validate."""
    prompt = TaskPrompt.model_validate(task_prompt_data)
