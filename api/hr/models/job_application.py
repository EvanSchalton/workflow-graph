"""
JobApplication model for HR management.
Represents applications linking resumes to job descriptions.
"""

from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator

if TYPE_CHECKING:
    from .job_description import JobDescription
    from .resume import Resume


class JobApplication(SQLModel, table=True):
    """
    JobApplication model representing applications from resumes to job descriptions.
    
    This model tracks the application process, including status changes,
    interview notes, and hiring decisions.
    """
    __tablename__ = "job_applications"
    
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Foreign keys
    job_description_id: int = Field(foreign_key="job_descriptions.id", description="Referenced job description")
    resume_id: int = Field(foreign_key="resumes.id", description="Referenced resume")
    
    # Application status and tracking
    status: str = Field(
        default="applied",
        max_length=50,
        description="Application status"
    )
    application_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the application was submitted"
    )
    
    # Optional fields for interview process
    interview_notes: Optional[str] = Field(default=None, description="Notes from interviews")
    hiring_decision_reason: Optional[str] = Field(default=None, description="Reason for hiring decision")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    job_description: Optional["JobDescription"] = Relationship(back_populates="job_applications")
    resume: Optional["Resume"] = Relationship(back_populates="job_applications")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate application status."""
        valid_statuses = {'applied', 'interviewing', 'hired', 'rejected'}
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v
    
    def __str__(self) -> str:
        """String representation of job application."""
        return f"JobApplication(id={self.id}, job_id={self.job_description_id}, resume_id={self.resume_id}, status='{self.status}')"
    
    def __repr__(self) -> str:
        """Detailed representation of job application."""
        return (
            f"JobApplication(id={self.id}, job_id={self.job_description_id}, "
            f"resume_id={self.resume_id}, status='{self.status}', "
            f"application_date={self.application_date.date()})"
        )
    
    def is_active(self) -> bool:
        """Check if application is still active (not hired or rejected)."""
        return self.status in {'applied', 'interviewing'}
    
    def can_transition_to(self, new_status: str) -> bool:
        """Check if status transition is valid."""
        valid_transitions = {
            'applied': {'interviewing', 'rejected'},
            'interviewing': {'hired', 'rejected'},
            'hired': set(),  # Terminal state
            'rejected': set()  # Terminal state
        }
        return new_status in valid_transitions.get(self.status, set())
    
    def update_status(self, new_status: str, reason: Optional[str] = None) -> bool:
        """
        Update application status with validation.
        Returns True if update was successful.
        """
        if not self.can_transition_to(new_status):
            return False
        
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        if new_status in {'hired', 'rejected'} and reason:
            self.hiring_decision_reason = reason
        
        return True


class JobApplicationCreate(SQLModel):
    """Schema for creating new job applications."""
    job_description_id: int
    resume_id: int
    status: str = "applied"
    interview_notes: Optional[str] = None


class JobApplicationUpdate(SQLModel):
    """Schema for updating existing job applications."""
    status: Optional[str] = None
    interview_notes: Optional[str] = None
    hiring_decision_reason: Optional[str] = None


class JobApplicationRead(SQLModel):
    """Schema for reading job applications."""
    id: int
    job_description_id: int
    resume_id: int
    status: str
    application_date: datetime
    interview_notes: Optional[str]
    hiring_decision_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
