"""
ResumePrompt model for prompt management.
Represents template prompts for generating agent personas and decision-making styles.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import field_validator, model_validator
import enum
import re
import string


class PersonaType(str, enum.Enum):
    """Valid persona types for agent generation."""
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    DETAIL_ORIENTED = "detail_oriented"
    COLLABORATIVE = "collaborative"
    LEADERSHIP = "leadership"
    TECHNICAL = "technical"
    PROBLEM_SOLVER = "problem_solver"
    COMMUNICATOR = "communicator"
    INNOVATOR = "innovator"
    MENTOR = "mentor"


class ResumePrompt(SQLModel, table=True):
    """
    Resume prompt model for agent persona generation.
    
    Stores reusable prompt templates for generating synthetic agent personas
    with different decision-making styles and behavioral characteristics.
    """
    __tablename__ = "resume_prompts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(
        description="Unique name for the resume prompt template"
    )
    description: Optional[str] = Field(
        default=None,
        description="Human-readable description of the persona type and characteristics"
    )
    prompt_template: str = Field(
        description="Template string for generating agent persona and behavioral traits"
    )
    variables: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
        description="List of variable names that can be substituted in the template"
    )
    persona_type: str = Field(
        description="Type of persona this prompt generates (e.g., 'analytical', 'creative', 'leadership')"
    )
    version: int = Field(
        default=1,
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

    @field_validator('persona_type')
    @classmethod
    def validate_persona_type(cls, v: str) -> str:
        """Validate and normalize persona_type field."""
        if not v or not v.strip():
            raise ValueError("Persona type cannot be empty")
        
        # Trim whitespace and normalize to lowercase with underscores
        v = v.strip().lower().replace(' ', '_').replace('-', '_')
        
        # Check for invalid characters
        if not re.match(r'^[a-z0-9_]+$', v):
            raise ValueError("Persona type contains invalid characters")
        
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

    @field_validator('version')
    @classmethod
    def validate_version(cls, v: int) -> int:
        """Validate version is positive."""
        if v < 1:
            raise ValueError("Version must be positive")
        return v

    @model_validator(mode='after')
    def validate_template_variables(self) -> 'ResumePrompt':
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

    def generate_persona_attributes(self) -> Dict[str, Any]:
        """
        Generate persona attributes based on the persona type.
        
        Returns:
            Dictionary of attributes typical for this persona type
        """
        persona_attributes = {
            PersonaType.ANALYTICAL: {
                "decision_style": "data_driven",
                "communication_style": "precise",
                "work_approach": "systematic",
                "strengths": ["logical_reasoning", "pattern_recognition", "risk_assessment"],
                "preferences": ["detailed_specifications", "clear_metrics", "structured_processes"]
            },
            PersonaType.CREATIVE: {
                "decision_style": "intuitive",
                "communication_style": "expressive", 
                "work_approach": "experimental",
                "strengths": ["innovation", "ideation", "design_thinking"],
                "preferences": ["flexible_deadlines", "brainstorming", "iterative_development"]
            },
            PersonaType.DETAIL_ORIENTED: {
                "decision_style": "thorough",
                "communication_style": "comprehensive",
                "work_approach": "methodical",
                "strengths": ["quality_assurance", "documentation", "process_improvement"],
                "preferences": ["complete_requirements", "testing", "verification"]
            },
            PersonaType.COLLABORATIVE: {
                "decision_style": "consensus_driven",
                "communication_style": "inclusive",
                "work_approach": "team_oriented",
                "strengths": ["facilitation", "conflict_resolution", "knowledge_sharing"],
                "preferences": ["group_work", "feedback_loops", "cross_functional_teams"]
            },
            PersonaType.LEADERSHIP: {
                "decision_style": "strategic",
                "communication_style": "inspiring",
                "work_approach": "goal_oriented",
                "strengths": ["vision_setting", "delegation", "performance_management"],
                "preferences": ["autonomy", "ownership", "results_tracking"]
            },
            PersonaType.TECHNICAL: {
                "decision_style": "evidence_based",
                "communication_style": "technical",
                "work_approach": "solution_focused",
                "strengths": ["problem_solving", "architecture", "optimization"],
                "preferences": ["technical_depth", "best_practices", "code_quality"]
            },
            PersonaType.PROBLEM_SOLVER: {
                "decision_style": "pragmatic",
                "communication_style": "direct",
                "work_approach": "solution_oriented",
                "strengths": ["root_cause_analysis", "troubleshooting", "critical_thinking"],
                "preferences": ["clear_problems", "quick_feedback", "practical_solutions"]
            },
            PersonaType.COMMUNICATOR: {
                "decision_style": "consultative",
                "communication_style": "engaging",
                "work_approach": "relationship_focused",
                "strengths": ["presentation", "documentation", "stakeholder_management"],
                "preferences": ["interaction", "feedback", "clarity"]
            },
            PersonaType.INNOVATOR: {
                "decision_style": "experimental",
                "communication_style": "visionary",
                "work_approach": "disruptive",
                "strengths": ["creativity", "research", "prototyping"],
                "preferences": ["exploration", "learning", "cutting_edge_tech"]
            },
            PersonaType.MENTOR: {
                "decision_style": "developmental",
                "communication_style": "supportive",
                "work_approach": "teaching_focused",
                "strengths": ["coaching", "knowledge_transfer", "skill_development"],
                "preferences": ["guidance_opportunities", "learning_culture", "growth_mindset"]
            }
        }
        
        # Try to match the persona_type to enum, fallback to generic attributes
        try:
            persona_enum = PersonaType(self.persona_type)
            return persona_attributes.get(persona_enum, {})
        except ValueError:
            # Return generic attributes for unknown persona types
            return {
                "decision_style": "balanced",
                "communication_style": "adaptive",
                "work_approach": "flexible",
                "strengths": ["adaptability", "learning", "collaboration"],
                "preferences": ["clear_expectations", "feedback", "growth_opportunities"]
            }

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "prompt_template": self.prompt_template,
            "variables": self.variables,
            "persona_type": self.persona_type,
            "version": self.version,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "persona_attributes": self.generate_persona_attributes()
        }

    model_config = {"from_attributes": True}  # type: ignore
