"""
JobDescription model for HR management.
Represents job descriptions used for hiring synthetic agents.
"""

from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY
from pydantic import field_validator, model_validator
import enum

if TYPE_CHECKING:
    from .job_application import JobApplication
    from .agent import Agent


class ExperienceLevel(str, enum.Enum):
    """Valid experience levels for job descriptions."""
    JUNIOR = "junior"
    MID = "mid" 
    SENIOR = "senior"
    LEAD = "lead"
    EXPERT = "expert"


class JobDescription(SQLModel, table=True):
    """
    Job description model for hiring synthetic agents.
    
    This model represents job descriptions that define the requirements
    for synthetic agents, including required skills, experience level,
    and department assignments.
    """
    __tablename__ = "job_descriptions"
    
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Required fields
    title: str = Field(min_length=1, max_length=255, description="Job title")
    description: str = Field(description="Detailed job description")
    required_skills: List[str] = Field(
        default_factory=list, 
        description="List of required skills for this position",
        sa_column=Column(ARRAY(String))
    )
    experience_level: ExperienceLevel = Field(description="Required experience level")
    
    # Optional fields
    department: Optional[str] = Field(
        default=None, 
        max_length=100, 
        description="Department for this position"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    job_applications: List["JobApplication"] = Relationship(
        back_populates="job_description",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    agents: List["Agent"] = Relationship(
        back_populates="job_description"
    )
    
    @field_validator('title', mode='before')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate that title is not empty and strip whitespace."""
        if not v or not v.strip():
            raise ValueError("Job title cannot be empty")
        return v.strip()
    
    @field_validator('required_skills', mode='before')
    @classmethod
    def validate_required_skills(cls, v) -> List[str]:
        """Validate and clean required_skills."""
        # Handle JSON string input
        if isinstance(v, str):
            try:
                import json
                v = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                raise ValueError("Required skills must be a list of strings")
        
        # Ensure it's a list
        if not isinstance(v, list):
            raise ValueError("Required skills must be a list")
        
        # Clean up skills - remove empty strings and strip whitespace
        cleaned_skills = [skill.strip() for skill in v if skill and skill.strip()]
        return cleaned_skills
    
    @field_validator('experience_level', mode='before')
    @classmethod 
    def validate_experience_level(cls, v) -> ExperienceLevel:
        """Validate that experience level is valid."""
        if isinstance(v, str):
            try:
                return ExperienceLevel(v.lower())
            except ValueError:
                valid_levels = [level.value for level in ExperienceLevel]
                raise ValueError(f"Experience level must be one of: {', '.join(valid_levels)}")
        return v
    
    def __str__(self) -> str:
        """String representation of job description."""
        return f"JobDescription(id={self.id}, title='{self.title}', level={self.experience_level.value})"
    
    def __repr__(self) -> str:
        """Detailed representation of job description."""
        return (
            f"JobDescription(id={self.id}, title='{self.title}', "
            f"experience_level='{self.experience_level.value}', "
            f"department='{self.department}', skills={len(self.required_skills)})"
        )
    
    def has_skill(self, skill: str) -> bool:
        """Check if job description requires a specific skill."""
        return skill.lower() in [s.lower() for s in self.required_skills]
    
    def add_skill(self, skill: str) -> None:
        """Add a required skill if not already present."""
        if not self.has_skill(skill):
            self.required_skills.append(skill.strip())
    
    def remove_skill(self, skill: str) -> bool:
        """Remove a required skill. Returns True if skill was removed."""
        for i, existing_skill in enumerate(self.required_skills):
            if existing_skill.lower() == skill.lower():
                self.required_skills.pop(i)
                return True
        return False
    
    def matches_skills(self, candidate_skills: List[str]) -> float:
        """
        Calculate how well candidate skills match job requirements.
        Returns a score between 0.0 and 1.0.
        """
        if not self.required_skills:
            return 1.0
        
        if not candidate_skills:
            return 0.0
        
        # Convert to lowercase for case-insensitive comparison
        required_lower = [skill.lower() for skill in self.required_skills]
        candidate_lower = [skill.lower() for skill in candidate_skills]
        
        # Count matching skills
        matches = sum(1 for skill in required_lower if skill in candidate_lower)
        
        # Return percentage of required skills that are matched
        return matches / len(required_lower)


class JobDescriptionCreate(SQLModel):
    """Schema for creating new job descriptions."""
    title: str = Field(min_length=1, max_length=255)
    description: str
    required_skills: List[str] = Field(default_factory=list)
    experience_level: ExperienceLevel
    department: Optional[str] = Field(default=None, max_length=100)


class JobDescriptionUpdate(SQLModel):
    """Schema for updating existing job descriptions."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    experience_level: Optional[ExperienceLevel] = None
    department: Optional[str] = Field(default=None, max_length=100)


class JobDescriptionRead(SQLModel):
    """Schema for reading job descriptions."""
    id: int
    title: str
    description: str
    required_skills: List[str]
    experience_level: ExperienceLevel
    department: Optional[str]
    created_at: datetime
    updated_at: datetime
