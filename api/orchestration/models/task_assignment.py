"""
TaskAssignment model for orchestration service.
Represents assignment of tasks to agents with cost and quality tracking.
"""

from typing import Optional, TYPE_CHECKING, ForwardRef
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator, model_validator
import enum

if TYPE_CHECKING:
    from .task import Task
    from ...hr.models.agent import Agent


class AssignmentStatus(str, enum.Enum):
    """Valid statuses for task assignments."""
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REASSIGNED = "reassigned"


class TaskAssignment(SQLModel, table=True):
    """
    Task assignment model linking agents to tasks.
    
    Tracks the assignment of specific tasks to agents including
    cost estimates, quality scores, and completion tracking.
    """
    __tablename__ = "task_assignments"
    
    # Primary identification
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Foreign key relationships
    task_id: int = Field(foreign_key="tasks.id", description="ID of the assigned task")
    agent_id: int = Field(foreign_key="agents.id", description="ID of the assigned agent")
    
    # Assignment tracking
    assigned_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when task was assigned to agent"
    )
    status: AssignmentStatus = Field(
        default=AssignmentStatus.ASSIGNED,
        description="Current status of the assignment"
    )
    
    # Performance and cost metrics
    capability_score: Decimal = Field(
        default=Decimal("0.0"),
        max_digits=5,
        decimal_places=2,
        ge=0.0,
        le=100.0,
        description="Agent's capability score for this task (0-100)"
    )
    cost_estimate: Optional[Decimal] = Field(
        default=None,
        max_digits=10,
        decimal_places=2,
        description="Estimated cost for agent to complete this task"
    )
    actual_cost: Optional[Decimal] = Field(
        default=None,
        max_digits=10,
        decimal_places=2,
        description="Actual cost incurred by agent for task completion"
    )
    
    # Quality and completion tracking
    completion_notes: Optional[str] = Field(
        default=None,
        description="Notes provided by agent upon task completion"
    )
    quality_score: Optional[Decimal] = Field(
        default=None,
        max_digits=5,
        decimal_places=2,
        ge=0.0,
        le=100.0,
        description="Quality assessment score for completed work (0-100)"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Assignment creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Assignment completion timestamp"
    )
    
    # Relationships
    task: "Task" = Relationship(back_populates="assignments")
    agent: "Agent" = Relationship(back_populates="assignments", sa_relationship_kwargs={"foreign_keys": "[TaskAssignment.agent_id]"})

    @field_validator('capability_score', 'quality_score', mode='before')
    @classmethod
    def validate_scores(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate score values are within valid range."""
        if v is not None:
            if v < 0 or v > 100:
                raise ValueError("Scores must be between 0 and 100")
        return v
    
    @field_validator('cost_estimate', 'actual_cost', mode='before')
    @classmethod
    def validate_costs(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate cost values are non-negative."""
        if v is not None and v < 0:
            raise ValueError("Costs cannot be negative")
        return v
    
    @model_validator(mode='after')
    def validate_assignment_constraints(self) -> 'TaskAssignment':
        """Validate assignment-level constraints."""
        # Validate completion timestamp logic
        if self.completed_at is not None and self.status not in [AssignmentStatus.COMPLETED, AssignmentStatus.FAILED]:
            raise ValueError("Completed timestamp can only be set for completed or failed assignments")
        
        # Quality score should only be set for completed assignments
        if self.quality_score is not None and self.status != AssignmentStatus.COMPLETED:
            raise ValueError("Quality score can only be set for completed assignments")
        
        # Actual cost should only be set for completed or failed assignments
        if self.actual_cost is not None and self.status not in [AssignmentStatus.COMPLETED, AssignmentStatus.FAILED]:
            raise ValueError("Actual cost can only be set for completed or failed assignments")
        
        return self
    
    def is_active(self) -> bool:
        """Check if assignment is currently active (not completed, failed, or reassigned)."""
        return self.status in [AssignmentStatus.ASSIGNED, AssignmentStatus.ACCEPTED, AssignmentStatus.IN_PROGRESS]
    
    def is_complete(self) -> bool:
        """Check if assignment has been completed successfully."""
        return self.status == AssignmentStatus.COMPLETED
    
    def update_status(self, new_status: AssignmentStatus, completion_notes: Optional[str] = None) -> None:
        """Update assignment status with proper timestamp handling."""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        # Set completion timestamp when transitioning to completed/failed
        if new_status in [AssignmentStatus.COMPLETED, AssignmentStatus.FAILED] and old_status not in [AssignmentStatus.COMPLETED, AssignmentStatus.FAILED]:
            self.completed_at = datetime.utcnow()
            if completion_notes:
                self.completion_notes = completion_notes
        
        # Clear completion timestamp when moving away from completed/failed
        elif old_status in [AssignmentStatus.COMPLETED, AssignmentStatus.FAILED] and new_status not in [AssignmentStatus.COMPLETED, AssignmentStatus.FAILED]:
            self.completed_at = None
    
    def set_quality_score(self, score: Decimal, notes: Optional[str] = None) -> None:
        """Set quality score for completed assignment."""
        if self.status != AssignmentStatus.COMPLETED:
            raise ValueError("Quality score can only be set for completed assignments")
        
        if score < 0 or score > 100:
            raise ValueError("Quality score must be between 0 and 100")
        
        self.quality_score = score
        if notes:
            self.completion_notes = notes
        self.updated_at = datetime.utcnow()
    
    def record_actual_cost(self, cost: Decimal) -> None:
        """Record actual cost for assignment."""
        if cost < 0:
            raise ValueError("Cost cannot be negative")
        
        self.actual_cost = cost
        self.updated_at = datetime.utcnow()
    
    def calculate_cost_efficiency(self) -> Optional[Decimal]:
        """Calculate cost efficiency as ratio of estimated to actual cost."""
        if self.cost_estimate is None or self.actual_cost is None or self.actual_cost == 0:
            return None
        
        return self.cost_estimate / self.actual_cost