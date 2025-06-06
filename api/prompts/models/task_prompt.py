"""
TaskPrompt model for prompt management.
Represents template prompts for different types of task execution.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import field_validator, model_validator
import re
import string


class TaskPrompt(SQLModel, table=True):
    """
    Task prompt model for template-based task execution.
    
    Stores reusable prompt templates with variable substitution support
    for different types of tasks in the agentic workforce system.
    """
    __tablename__ = "task_prompts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(
        description="Unique name for the task prompt template"
    )
    description: Optional[str] = Field(
        default=None,
        description="Human-readable description of the prompt's purpose"
    )
    prompt_template: str = Field(
        description="Template string with variable placeholders for task execution"
    )
    variables: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
        description="List of variable names that can be substituted in the template"
    )
    task_type: str = Field(
        description="Type of task this prompt is designed for (e.g., 'code_review', 'documentation', 'testing')"
    )
    version: int = Field(
        default=1,
        ge=1,
        description="Version number for prompt template evolution and A/B testing"
    )
    is_active: bool = Field(
        default=True,
        description="Whether this prompt template is currently active and available for use"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this prompt template was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this prompt template was last modified"
    )

    def substitute_variables(self, **kwargs: Any) -> str:
        """
        Substitute variables in the prompt template with provided values.
        
        Args:
            **kwargs: Variable name-value pairs for substitution
            
        Returns:
            The prompt template with variables substituted
            
        Raises:
            ValueError: If required variables are missing or invalid values provided
        """
        if not self.prompt_template:
            return ""
        
        # Check for missing required variables
        provided_vars = set(kwargs.keys())
        required_vars = set(self.variables)
        missing_vars = required_vars - provided_vars
        
        if missing_vars:
            raise ValueError(f"Missing required variables: {sorted(missing_vars)}")
        
        # Check for extra variables
        extra_vars = provided_vars - required_vars
        if extra_vars:
            raise ValueError(f"Unknown variables provided: {sorted(extra_vars)}")
        
        try:
            return self.prompt_template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Template substitution failed: {e}")
        except Exception as e:
            raise ValueError(f"Template formatting error: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "prompt_template": self.prompt_template,
            "variables": self.variables,
            "task_type": self.task_type,
            "version": self.version,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and normalize name field."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        
        # Trim whitespace
        v = v.strip()
        
        # Check for invalid characters
        if not re.match(r'^[a-zA-Z0-9_\-\s]+$', v):
            raise ValueError("Name contains invalid characters")
        
        return v

    @field_validator('task_type')
    @classmethod
    def validate_task_type(cls, v: str) -> str:
        """Validate and normalize task_type field."""
        if not v or not v.strip():
            raise ValueError("Task type cannot be empty")
        
        # Trim whitespace and normalize to lowercase with underscores
        v = v.strip().lower().replace(' ', '_')
        
        # Check for invalid characters
        if not re.match(r'^[a-z0-9_]+$', v):
            raise ValueError("Task type contains invalid characters")
        
        return v

    @field_validator('prompt_template')
    @classmethod
    def validate_prompt_template(cls, v: str) -> str:
        """Validate and normalize prompt_template field."""
        if not v or not v.strip():
            raise ValueError("Prompt template cannot be empty")
        
        # Trim whitespace
        v = v.strip()
        
        return v

    @field_validator('variables')
    @classmethod
    def validate_variables(cls, v: List[str]) -> List[str]:
        """Validate and normalize variables field."""
        if not isinstance(v, list):
            raise ValueError("Variables must be a list")
        
        # Validate each variable
        validated_vars = []
        for var in v:
            if not isinstance(var, str):
                raise ValueError("Each variable must be a string")
            
            var = var.strip()
            if not var:
                raise ValueError("Variable names cannot be empty")
            
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var):
                raise ValueError(f"Invalid variable name: {var}")
            
            validated_vars.append(var)
        
        # Remove duplicates while preserving order
        seen = set()
        deduplicated = []
        for var in validated_vars:
            if var not in seen:
                seen.add(var)
                deduplicated.append(var)
        
        return deduplicated

    @model_validator(mode='after')
    def validate_template_variables(self) -> 'TaskPrompt':
        """Validate that template variables match declared variables."""
        if not self.prompt_template:
            return self
        
        # Extract variables from template using string.Formatter
        formatter = string.Formatter()
        template_vars = set()
        
        try:
            for literal_text, field_name, format_spec, conversion in formatter.parse(self.prompt_template):
                if field_name is not None:
                    template_vars.add(field_name)
        except Exception:
            raise ValueError("Invalid template format")
        
        declared_vars = set(self.variables)
        
        # Check for undeclared variables in template
        undeclared = template_vars - declared_vars
        if undeclared:
            raise ValueError(f"Template uses undeclared variables: {sorted(undeclared)}")
        
        return self

    model_config = {"from_attributes": True}  # type: ignore
