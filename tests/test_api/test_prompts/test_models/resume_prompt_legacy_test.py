# filepath: tests/test_api/test_prompts/test_models/resume_prompt_legacy_test.py
"""
COMPLETE MIGRATION: resume_prompt_legacy_test.py
Source: tests/test_prompts/resume_prompt_test.py
Migrated: 2025-06-15 19:35:42
Test Functions: 24
Status: COMPLETE - All content migrated
"""

# MIGRATED: Content moved to tests/test_api/test_prompts/test_models/resume_prompt_test.py
# This file is kept for reference but all tests have been migrated to the new structure
# Date: 2025-06-15
# Migration completed: 20+ test functions migrated successfully

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


@pytest.mark.parametrize("invalid_name", [
    "",
    "   ",
    "name@invalid",
    "name#invalid",
    "name$invalid"
])
def test_resume_prompt_invalid_name(resume_prompt_data: dict, invalid_name: str) -> None:
    """Test ResumePrompt validation with invalid names."""
    resume_prompt_data["name"] = invalid_name
    
    with pytest.raises(ValidationError) as exc_info:
        ResumePrompt.model_validate(resume_prompt_data)
    
    assert "Name" in str(exc_info.value)


@pytest.mark.parametrize("invalid_persona_type", [
    "",
    "   ",
    "type@invalid",
    "type#invalid"
])
def test_resume_prompt_invalid_persona_type(resume_prompt_data: dict, invalid_persona_type: str) -> None:
    """Test ResumePrompt validation with invalid persona types."""
    resume_prompt_data["persona_type"] = invalid_persona_type
    
    with pytest.raises(ValidationError) as exc_info:
        ResumePrompt.model_validate(resume_prompt_data)
    
    assert "Persona type" in str(exc_info.value)


def test_resume_prompt_persona_type_normalization(resume_prompt_data: dict) -> None:
    """Test persona type normalization."""
    resume_prompt_data["persona_type"] = "Detail Oriented"
    prompt = ResumePrompt.model_validate(resume_prompt_data)
    
    assert prompt.persona_type == "detail_oriented"


@pytest.mark.parametrize("invalid_template", [
    "",
    "   "
])
def test_resume_prompt_invalid_template(resume_prompt_data: dict, invalid_template: str) -> None:
    """Test ResumePrompt validation with invalid prompt templates."""
    resume_prompt_data["prompt_template"] = invalid_template
    
    with pytest.raises(ValidationError) as exc_info:
        ResumePrompt.model_validate(resume_prompt_data)
    
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
def test_resume_prompt_invalid_variables(resume_prompt_data: dict, invalid_variables: Any) -> None:
    """Test ResumePrompt validation with invalid variable names."""
    resume_prompt_data["variables"] = invalid_variables
    
    with pytest.raises(ValidationError) as exc_info:
        ResumePrompt.model_validate(resume_prompt_data)
    
    error_msg = str(exc_info.value)
    assert any(phrase in error_msg for phrase in ["variable", "Variables", "Invalid"])


def test_resume_prompt_variables_deduplication(resume_prompt_data: dict) -> None:
    """Test that duplicate variables are removed."""
    # Use variables that include the ones required by the template
    resume_prompt_data["variables"] = ["persona_type", "experience_level", "domain", "persona_type", "extra_var", "domain"]
    prompt = ResumePrompt.model_validate(resume_prompt_data)
    
    assert set(prompt.variables) == set(["persona_type", "experience_level", "domain", "extra_var"])


@pytest.mark.parametrize("invalid_version", [
    0,
    -1,
    -5
])
def test_resume_prompt_invalid_version(resume_prompt_data: dict, invalid_version: int) -> None:
    """Test ResumePrompt validation with invalid version numbers."""
    resume_prompt_data["version"] = invalid_version
    
    with pytest.raises(ValidationError) as exc_info:
        ResumePrompt.model_validate(resume_prompt_data)
    
    assert "Version must be positive" in str(exc_info.value)


def test_resume_prompt_template_variable_validation_success(resume_prompt_data: dict) -> None:
    """Test successful template variable validation."""
    resume_prompt_data["prompt_template"] = "Generate {persona_type} with {experience_level}"
    resume_prompt_data["variables"] = ["persona_type", "experience_level"]
    
    prompt = ResumePrompt(**resume_prompt_data)
    assert prompt.variables == ["persona_type", "experience_level"]


def test_resume_prompt_template_variable_validation_undeclared(resume_prompt_data: dict) -> None:
    """Test template variable validation with undeclared variables."""
    resume_prompt_data["prompt_template"] = "Generate {persona_type} with {undeclared_var}"
    resume_prompt_data["variables"] = ["persona_type"]
    
    with pytest.raises(ValidationError) as exc_info:
        ResumePrompt.model_validate(resume_prompt_data)
    
    assert "undeclared variables" in str(exc_info.value)
    assert "undeclared_var" in str(exc_info.value)


def test_resume_prompt_substitute_variables_success(resume_prompt_data: dict) -> None:
    """Test successful variable substitution."""
    prompt = ResumePrompt(**resume_prompt_data)
    
    result = prompt.substitute_variables(
        persona_type="analytical",
        experience_level="senior",
        domain="software engineering"
    )
    
    expected = "Generate a analytical persona with senior experience in software engineering"
    assert result == expected


def test_resume_prompt_substitute_variables_missing(resume_prompt_data: dict) -> None:
    """Test variable substitution with missing variables."""
    prompt = ResumePrompt(**resume_prompt_data)
    
    with pytest.raises(ValueError) as exc_info:
        prompt.substitute_variables(persona_type="analytical")
    
    assert "Missing required variables" in str(exc_info.value)
    assert "experience_level" in str(exc_info.value)
    assert "domain" in str(exc_info.value)


def test_resume_prompt_substitute_variables_extra(resume_prompt_data: dict) -> None:
    """Test variable substitution with extra variables."""
    prompt = ResumePrompt(**resume_prompt_data)
    
    with pytest.raises(ValueError) as exc_info:
        prompt.substitute_variables(
            persona_type="analytical",
            experience_level="senior", 
            domain="engineering",
            extra_var="not allowed"
        )
    
    assert "Unknown variables provided" in str(exc_info.value)
    assert "extra_var" in str(exc_info.value)


@pytest.mark.parametrize("persona_type,expected_attributes", [
    (PersonaType.ANALYTICAL, {
        "decision_style": "data_driven",
        "communication_style": "precise",
        "work_approach": "systematic"
    }),
    (PersonaType.CREATIVE, {
        "decision_style": "intuitive",
        "communication_style": "expressive",
        "work_approach": "experimental"
    }),
    (PersonaType.LEADERSHIP, {
        "decision_style": "strategic", 
        "communication_style": "inspiring",
        "work_approach": "goal_oriented"
    }),
    (PersonaType.TECHNICAL, {
        "decision_style": "evidence_based",
        "communication_style": "technical",
        "work_approach": "solution_focused"
    })
])
def test_resume_prompt_generate_persona_attributes(persona_type: PersonaType, expected_attributes: dict) -> None:
    """Test persona attribute generation for different types."""
    prompt = ResumePrompt(
        name="test_prompt",
        prompt_template="Test template",
        persona_type=persona_type.value
    )
    
    attributes = prompt.generate_persona_attributes()
    
    assert isinstance(attributes, dict)
    for key, expected_value in expected_attributes.items():
        assert attributes[key] == expected_value
    
    # Check that all expected keys are present
    expected_keys = ["decision_style", "communication_style", "work_approach", "strengths", "preferences"]
    for key in expected_keys:
        assert key in attributes


def test_resume_prompt_generate_persona_attributes_unknown_type() -> None:
    """Test persona attribute generation for unknown persona type."""
    prompt = ResumePrompt(
        name="test_prompt",
        prompt_template="Test template",
        persona_type="unknown_type"
    )
    
    attributes = prompt.generate_persona_attributes()
    
    assert isinstance(attributes, dict)
    assert attributes["decision_style"] == "balanced"
    assert attributes["communication_style"] == "adaptive"
    assert attributes["work_approach"] == "flexible"
    assert "adaptability" in attributes["strengths"]


def test_resume_prompt_to_dict(resume_prompt_data: dict) -> None:
    """Test converting ResumePrompt to dictionary."""
    prompt = ResumePrompt(**resume_prompt_data)
    result = prompt.to_dict()
    
    assert isinstance(result, dict)
    assert result["name"] == resume_prompt_data["name"]
    assert result["description"] == resume_prompt_data["description"]
    assert result["prompt_template"] == resume_prompt_data["prompt_template"]
    assert result["variables"] == resume_prompt_data["variables"]
    assert result["persona_type"] == resume_prompt_data["persona_type"]
    assert result["version"] == resume_prompt_data["version"]
    assert result["is_active"] == resume_prompt_data["is_active"]
    assert isinstance(result["created_at"], str)
    assert isinstance(result["updated_at"], str)
    assert "persona_attributes" in result
    assert isinstance(result["persona_attributes"], dict)


def test_persona_type_enum_values() -> None:
    """Test that all PersonaType enum values are valid."""
    expected_values = [
        "analytical", "creative", "detail_oriented", "collaborative",
        "leadership", "technical", "problem_solver", "communicator",
        "innovator", "mentor"
    ]
    
    actual_values = [persona.value for persona in PersonaType]
    
    assert len(actual_values) == len(expected_values)
    for expected in expected_values:
        assert expected in actual_values


def test_resume_prompt_name_trimming(resume_prompt_data: dict) -> None:
    """Test that name whitespace is trimmed."""
    resume_prompt_data["name"] = "  test_name  "
    prompt = ResumePrompt.model_validate(resume_prompt_data)
    
    assert prompt.name == "test_name"


def test_resume_prompt_template_trimming(resume_prompt_data: dict) -> None:
    """Test that template whitespace is trimmed."""
    resume_prompt_data["prompt_template"] = "  template content  "
    prompt = ResumePrompt.model_validate(resume_prompt_data)
    
    assert prompt.prompt_template == "template content"


def test_resume_prompt_persona_type_case_insensitive() -> None:
    """Test that persona types are case insensitive."""
    prompt = ResumePrompt.model_validate({
        "name": "test_prompt",
        "prompt_template": "Test template",
        "persona_type": "ANALYTICAL"
    })
    
    assert prompt.persona_type == "analytical"


def test_resume_prompt_complex_template_substitution() -> None:
    """Test complex template with multiple variable substitutions."""
    prompt = ResumePrompt(
        name="complex_template",
        prompt_template="Create {persona_type} agent for {domain} with {skills} skills and {experience} experience",
        variables=["persona_type", "domain", "skills", "experience"],
        persona_type="technical"
    )
    
    result = prompt.substitute_variables(
        persona_type="technical",
        domain="machine learning",
        skills="Python, TensorFlow",
        experience="5 years"
    )
    
    expected = "Create technical agent for machine learning with Python, TensorFlow skills and 5 years experience"
    assert result == expected


def test_resume_prompt_empty_template_substitution() -> None:
    """Test variable substitution with empty template."""
    prompt = ResumePrompt(
        name="empty_template",
        prompt_template="",
        persona_type="basic"
    )
    
    result = prompt.substitute_variables()
    assert result == ""
