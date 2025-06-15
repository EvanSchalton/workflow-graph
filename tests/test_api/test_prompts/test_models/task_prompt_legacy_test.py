# filepath: tests/test_api/test_prompts/test_models/task_prompt_legacy_test.py
"""
COMPLETE MIGRATION: task_prompt_legacy_test.py
Source: tests/test_prompts/task_prompt_test.py
Migrated: 2025-06-15 19:35:42
Test Functions: 21
Status: COMPLETE - All content migrated
"""

# MIGRATED: Content moved to tests/test_api/test_prompts/test_models/task_prompt_test.py
# This file is kept for reference but all tests have been migrated to the new structure
# Date: 2025-06-15
# Migration completed: 15+ test functions migrated successfully

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
    
    assert prompt.name == task_prompt_data["name"]
    assert prompt.task_type == task_prompt_data["task_type"]


def test_task_prompt_defaults() -> None:
    """Test TaskPrompt with minimal required fields."""
    prompt = TaskPrompt(
        name="minimal_prompt",
        prompt_template="Simple template",
        task_type="basic"
    )
    
    assert prompt.name == "minimal_prompt"
    assert prompt.description is None
    assert prompt.variables == []
    assert prompt.version == 1
    assert prompt.is_active is True
    assert isinstance(prompt.created_at, datetime)
    assert isinstance(prompt.updated_at, datetime)


@pytest.mark.parametrize("invalid_name", [
    "",
    "   ",
    "name@invalid",
    "name#invalid",
    "name$invalid"
])
def test_task_prompt_invalid_name(task_prompt_data: dict, invalid_name: str) -> None:
    """Test TaskPrompt validation with invalid names."""
    task_prompt_data["name"] = invalid_name
    
    with pytest.raises(ValidationError) as exc_info:
        TaskPrompt.model_validate(task_prompt_data)
    
    assert "Name" in str(exc_info.value)


@pytest.mark.parametrize("invalid_task_type", [
    "",
    "   ",
    "type@invalid",
    "type#invalid"
])
def test_task_prompt_invalid_task_type(task_prompt_data: dict, invalid_task_type: str) -> None:
    """Test TaskPrompt validation with invalid task types."""
    task_prompt_data["task_type"] = invalid_task_type
    
    with pytest.raises(ValidationError) as exc_info:
        TaskPrompt.model_validate(task_prompt_data)
    
    assert "Task type" in str(exc_info.value)


def test_task_prompt_task_type_normalization(task_prompt_data: dict) -> None:
    """Test task type normalization."""
    task_prompt_data["task_type"] = "Code Review"
    prompt = TaskPrompt.model_validate(task_prompt_data)
    
    assert prompt.task_type == "code_review"


@pytest.mark.parametrize("invalid_template", [
    "",
    "   "
])
def test_task_prompt_invalid_template(task_prompt_data: dict, invalid_template: str) -> None:
    """Test TaskPrompt validation with invalid prompt templates."""
    task_prompt_data["prompt_template"] = invalid_template
    
    with pytest.raises(ValidationError) as exc_info:
        TaskPrompt.model_validate(task_prompt_data)
    
    assert "Prompt template" in str(exc_info.value)


@pytest.mark.parametrize("invalid_variables", [
    [""],
    ["valid", ""],
    ["123invalid"],
    ["invalid-name"],
    ["invalid name"],
    [123],
    "not_a_list"
])
def test_task_prompt_invalid_variables(task_prompt_data: dict, invalid_variables: Any) -> None:
    """Test TaskPrompt validation with invalid variable names."""
    task_prompt_data["variables"] = invalid_variables
    
    with pytest.raises(ValidationError) as exc_info:
        TaskPrompt.model_validate(task_prompt_data)
    
    error_msg = str(exc_info.value)
    assert any(phrase in error_msg for phrase in ["variable", "Variables", "Invalid"])


def test_task_prompt_variables_deduplication(task_prompt_data: dict) -> None:
    """Test that duplicate variables are removed."""
    # Use variables that include the ones required by the template
    task_prompt_data["variables"] = ["task_description", "parameters", "task_description", "extra_var", "parameters"]
    prompt = TaskPrompt.model_validate(task_prompt_data)
    
    assert set(prompt.variables) == set(["task_description", "parameters", "extra_var"])


@pytest.mark.parametrize("invalid_version", [
    0,
    -1,
    -5
])
def test_task_prompt_invalid_version(task_prompt_data: dict, invalid_version: int) -> None:
    """Test TaskPrompt validation with invalid version numbers."""
    task_prompt_data["version"] = invalid_version
    
    with pytest.raises(ValidationError) as exc_info:
        TaskPrompt.model_validate(task_prompt_data)
    
    assert "greater than or equal to 1" in str(exc_info.value)


def test_task_prompt_template_variable_validation_success(task_prompt_data: dict) -> None:
    """Test successful template variable validation."""
    task_prompt_data["prompt_template"] = "Task: {task_description} with {parameters}"
    task_prompt_data["variables"] = ["task_description", "parameters"]
    
    prompt = TaskPrompt(**task_prompt_data)
    assert prompt.variables == ["task_description", "parameters"]


def test_task_prompt_template_variable_validation_undeclared(task_prompt_data: dict) -> None:
    """Test template variable validation with undeclared variables."""
    task_prompt_data["prompt_template"] = "Task: {task_description} with {undeclared_var}"
    task_prompt_data["variables"] = ["task_description"]
    
    with pytest.raises(ValidationError) as exc_info:
        TaskPrompt.model_validate(task_prompt_data)
    
    assert "undeclared variables" in str(exc_info.value)
    assert "undeclared_var" in str(exc_info.value)


def test_task_prompt_template_variable_validation_unused(task_prompt_data: dict) -> None:
    """Test template variable validation with unused declared variables."""
    task_prompt_data["prompt_template"] = "Task: {task_description}"
    task_prompt_data["variables"] = ["task_description", "unused_var"]
    
    # Should not raise an error - unused variables are allowed
    prompt = TaskPrompt(**task_prompt_data)
    assert prompt.variables == ["task_description", "unused_var"]


def test_task_prompt_substitute_variables_success(task_prompt_data: dict) -> None:
    """Test successful variable substitution."""
    prompt = TaskPrompt(**task_prompt_data)
    
    result = prompt.substitute_variables(
        task_description="Review code",
        parameters="with focus on security"
    )
    
    expected = "Execute task: Review code with parameters: with focus on security"
    assert result == expected


def test_task_prompt_substitute_variables_missing(task_prompt_data: dict) -> None:
    """Test variable substitution with missing variables."""
    prompt = TaskPrompt(**task_prompt_data)
    
    with pytest.raises(ValueError) as exc_info:
        prompt.substitute_variables(task_description="Review code")
    
    assert "Missing required variables" in str(exc_info.value)
    assert "parameters" in str(exc_info.value)


def test_task_prompt_substitute_variables_extra(task_prompt_data: dict) -> None:
    """Test variable substitution with extra variables."""
    prompt = TaskPrompt(**task_prompt_data)
    
    with pytest.raises(ValueError) as exc_info:
        prompt.substitute_variables(
            task_description="Review code",
            parameters="with focus",
            extra_var="not allowed"
        )
    
    assert "Unknown variables provided" in str(exc_info.value)
    assert "extra_var" in str(exc_info.value)


def test_task_prompt_substitute_variables_empty_template() -> None:
    """Test variable substitution with empty template."""
    prompt = TaskPrompt(
        name="empty_template",
        prompt_template="",
        task_type="basic"
    )
    
    result = prompt.substitute_variables()
    assert result == ""


def test_task_prompt_to_dict(task_prompt_data: dict) -> None:
    """Test converting TaskPrompt to dictionary."""
    prompt = TaskPrompt(**task_prompt_data)
    result = prompt.to_dict()
    
    assert isinstance(result, dict)
    assert result["name"] == task_prompt_data["name"]
    assert result["description"] == task_prompt_data["description"]
    assert result["prompt_template"] == task_prompt_data["prompt_template"]
    assert result["variables"] == task_prompt_data["variables"]
    assert result["task_type"] == task_prompt_data["task_type"]
    assert result["version"] == task_prompt_data["version"]
    assert result["is_active"] == task_prompt_data["is_active"]
    assert isinstance(result["created_at"], str)
    assert isinstance(result["updated_at"], str)


def test_task_prompt_name_trimming(task_prompt_data: dict) -> None:
    """Test that name whitespace is trimmed."""
    task_prompt_data["name"] = "  test_name  "
    prompt = TaskPrompt.model_validate(task_prompt_data)
    
    assert prompt.name == "test_name"


def test_task_prompt_template_trimming(task_prompt_data: dict) -> None:
    """Test that template whitespace is trimmed."""
    task_prompt_data["prompt_template"] = "  template content  "
    prompt = TaskPrompt.model_validate(task_prompt_data)
    
    assert prompt.prompt_template == "template content"


def test_task_prompt_complex_template_substitution() -> None:
    """Test complex template with multiple variable substitutions."""
    prompt = TaskPrompt(
        name="complex_template",
        prompt_template="Execute {action} on {target} using {method} with {priority} priority",
        variables=["action", "target", "method", "priority"],
        task_type="complex"
    )
    
    result = prompt.substitute_variables(
        action="deploy",
        target="production",
        method="blue-green",
        priority="high"
    )
    
    expected = "Execute deploy on production using blue-green with high priority"
    assert result == expected
