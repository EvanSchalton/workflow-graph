"""
Resume model for HR management.
Represents synthetic resumes for agent workforce.
"""

import re
import json
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from pydantic import field_validator
from dateutil.parser import parse as parse_date

if TYPE_CHECKING:
    from .job_application import JobApplication
    from .agent import Agent


class ExperienceEntry(SQLModel):
    """Model for work experience entries."""
    company: str = Field(description="Company name")
    position: str = Field(description="Job position/title") 
    start_date: str = Field(description="Start date (YYYY-MM-DD format)")
    end_date: Optional[str] = Field(default=None, description="End date (YYYY-MM-DD format), None if current")
    description: Optional[str] = Field(default=None, description="Job description and responsibilities")


class EducationEntry(SQLModel):
    """Model for education entries."""
    institution: str = Field(description="Educational institution name")
    degree: str = Field(description="Degree type (e.g., Bachelor of Science)")
    field_of_study: Optional[str] = Field(default=None, description="Field of study")
    graduation_year: int = Field(description="Year of graduation")
    gpa: Optional[float] = Field(default=None, description="GPA if available")


class Resume(SQLModel, table=True):
    """
    Resume model for synthetic agents.
    
    This model represents synthetic resumes that can be generated
    for agent workforce management, including skills, experience,
    and performance tracking.
    """
    __tablename__ = "resumes"
    
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Required fields
    name: str = Field(min_length=1, max_length=255, description="Full name")
    email: str = Field(max_length=255, description="Email address")
    
    # Optional contact fields
    phone: Optional[str] = Field(default=None, max_length=50, description="Phone number")
    
    # Profile information
    summary: Optional[str] = Field(default=None, description="Professional summary")
    
    # Skills and experience
    skills: List[str] = Field(
        default_factory=list,
        description="List of technical and soft skills",
        sa_column=Column(ARRAY(String))
    )
    
    # JSON fields for complex data
    experience: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Work experience entries",
        sa_column=Column(JSONB)
    )
    
    education: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Education entries", 
        sa_column=Column(JSONB)
    )
    
    performance_history: Dict[str, Any] = Field(
        default_factory=dict,
        description="Performance metrics and history",
        sa_column=Column(JSONB)
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    job_applications: List["JobApplication"] = Relationship(
        back_populates="resume",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    agent: Optional["Agent"] = Relationship(back_populates="resume")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that name is not empty and strip whitespace."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
    
    @field_validator('email') 
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        v = v.strip()  # Strip whitespace first
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()
    
    @field_validator('skills')
    @classmethod
    def validate_skills(cls, v) -> List[str]:
        """Validate and clean skills list."""
        # Handle JSON string input
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                raise ValueError("Skills must be a list of strings")
        
        # Ensure it's a list
        if not isinstance(v, list):
            raise ValueError("Skills must be a list")
        
        # Clean up skills - remove empty strings and strip whitespace
        cleaned_skills = [skill.strip() for skill in v if skill and skill.strip()]
        return cleaned_skills
    
    @field_validator('experience')
    @classmethod
    def validate_experience(cls, v) -> List[Dict[str, Any]]:
        """Validate experience entries."""
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                raise ValueError("Experience must be a list of objects")
        
        if not isinstance(v, list):
            raise ValueError("Experience must be a list")
        
        return v
    
    @field_validator('education')
    @classmethod
    def validate_education(cls, v) -> List[Dict[str, Any]]:
        """Validate education entries."""
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                raise ValueError("Education must be a list of objects")
        
        if not isinstance(v, list):
            raise ValueError("Education must be a list")
        
        return v
    
    @field_validator('performance_history')
    @classmethod
    def validate_performance_history(cls, v) -> Dict[str, Any]:
        """Validate performance history."""
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                raise ValueError("Performance history must be a JSON object")
        
        if not isinstance(v, dict):
            raise ValueError("Performance history must be a dictionary")
        
        return v
    
    def __str__(self) -> str:
        """String representation of resume."""
        return f"Resume(id={self.id}, name='{self.name}', email='{self.email}')"
    
    def __repr__(self) -> str:
        """Detailed representation of resume."""
        return (
            f"Resume(id={self.id}, name='{self.name}', email='{self.email}', "
            f"skills={len(self.skills)}, experience={len(self.experience)})"
        )
    
    def has_skill(self, skill: str) -> bool:
        """Check if resume contains a specific skill (case insensitive)."""
        return skill.lower() in [s.lower() for s in self.skills]
    
    def add_skill(self, skill: str) -> None:
        """Add a skill if not already present."""
        if not self.has_skill(skill):
            self.skills.append(skill.strip())
    
    def remove_skill(self, skill: str) -> bool:
        """Remove a skill. Returns True if skill was removed."""
        for i, existing_skill in enumerate(self.skills):
            if existing_skill.lower() == skill.lower():
                self.skills.pop(i)
                return True
        return False
    
    def calculate_experience_years(self) -> float:
        """Calculate total years of experience from experience entries."""
        total_days = 0
        
        for exp in self.experience:
            try:
                start_date = parse_date(exp['start_date']).date()
                
                if exp.get('end_date'):
                    end_date = parse_date(exp['end_date']).date()
                else:
                    end_date = date.today()
                
                days = (end_date - start_date).days
                total_days += max(0, days)  # Ensure non-negative
                
            except (KeyError, ValueError, TypeError):
                # Skip invalid experience entries
                continue
        
        return round(total_days / 365.25, 1)  # Account for leap years
    
    def skill_match_score(self, required_skills: List[str]) -> float:
        """
        Calculate how well resume skills match required skills.
        Returns a score between 0.0 and 1.0.
        """
        if not required_skills:
            return 1.0
        
        if not self.skills:
            return 0.0
        
        # Convert to lowercase for case-insensitive comparison
        resume_skills_lower = [skill.lower() for skill in self.skills]
        required_skills_lower = [skill.lower() for skill in required_skills]
        
        # Count matching skills
        matches = sum(1 for skill in required_skills_lower if skill in resume_skills_lower)
        
        # Return percentage of required skills that are matched
        return matches / len(required_skills_lower)


class ResumeCreate(SQLModel):
    """Schema for creating new resumes."""
    name: str = Field(min_length=1, max_length=255)
    email: str = Field(max_length=255)
    phone: Optional[str] = Field(default=None, max_length=50)
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    performance_history: Dict[str, Any] = Field(default_factory=dict)


class ResumeUpdate(SQLModel):
    """Schema for updating existing resumes."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=50)
    summary: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    performance_history: Optional[Dict[str, Any]] = None


class ResumeRead(SQLModel):
    """Schema for reading resumes."""
    id: int
    name: str
    email: str
    phone: Optional[str]
    summary: Optional[str]
    skills: List[str]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    performance_history: Dict[str, Any]
    created_at: datetime
    updated_at: datetime