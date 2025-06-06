"""
Task model for orchestration service.
Represents tasks that can be assigned to agents with dependency tracking.
"""

from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from pydantic import field_validator, model_validator
import enum

if TYPE_CHECKING:
    from .task_assignment import TaskAssignment


class TaskStatus(str, enum.Enum):
    """Valid statuses for tasks."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(str, enum.Enum):
    """Valid priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(SQLModel, table=True):
    """
    Task model for orchestrating work assignments.
    
    Tasks represent work items that can be broken down from JIRA tickets
    or created directly. They support dependency tracking, cost estimation,
    and hierarchical relationships through parent_task_id.
    """
    __tablename__ = "tasks"
    
    # Primary identification
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255, description="Short descriptive title for the task")
    description: str = Field(description="Detailed description of what needs to be done")
    
    # External references
    jira_task_id: Optional[str] = Field(
        default=None, 
        max_length=100,
        description="Reference to originating JIRA task ID"
    )
    parent_task_id: Optional[int] = Field(
        default=None,
        foreign_key="tasks.id",
        description="Reference to parent task for sub-task relationships"
    )
    
    # Status and priority
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current task status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority level")
    
    # Skills and requirements
    required_skills: List[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(String)),
        description="List of skills required to complete this task"
    )
    
    # Cost tracking
    estimated_cost: Optional[Decimal] = Field(
        default=None,
        max_digits=10,
        decimal_places=2,
        description="Estimated cost to complete this task"
    )
    actual_cost: Optional[Decimal] = Field(
        default=None,
        max_digits=10,
        decimal_places=2,
        description="Actual cost incurred for task completion"
    )
    
    # Dependency and blocker tracking
    dependencies: List[int] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
        description="List of task IDs that must be completed before this task"
    )
    blockers: List[Dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
        description="List of blocker objects with type, description, and resolution info"
    )
    
    # Additional metadata
    task_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB),
        description="Flexible metadata storage for task-specific information"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Task creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Task completion timestamp")
    deadline: Optional[datetime] = Field(default=None, description="Task deadline if specified")
    
    # Relationships
    assignments: List["TaskAssignment"] = Relationship(
        back_populates="task",
        cascade_delete=True
    )
    # Note: execution_costs relationship is defined via foreign keys
    # to avoid circular import issues during SQLAlchemy mapper initialization
    
    # Self-referential relationship for parent/child tasks
    subtasks: List["Task"] = Relationship(
        back_populates="parent_task"
    )
    parent_task: Optional["Task"] = Relationship(
        back_populates="subtasks",
        sa_relationship_kwargs={"remote_side": "Task.id"}
    )

    @field_validator('required_skills')
    @classmethod
    def validate_required_skills(cls, v: List[str]) -> List[str]:
        """Validate required skills list."""
        if not isinstance(v, list):
            raise ValueError("Required skills must be a list")
        
        # Remove duplicates and empty strings
        skills = [skill.strip() for skill in v if skill.strip()]
        return list(set(skills))
    
    @field_validator('dependencies')
    @classmethod
    def validate_dependencies(cls, v: List[int]) -> List[int]:
        """Validate dependencies list."""
        if not isinstance(v, list):
            raise ValueError("Dependencies must be a list")
        
        # Ensure all dependencies are positive integers
        for dep_id in v:
            if not isinstance(dep_id, int) or dep_id <= 0:
                raise ValueError("All dependency IDs must be positive integers")
        
        # Remove duplicates
        return list(set(v))
    
    @field_validator('blockers')
    @classmethod
    def validate_blockers(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate blockers list structure."""
        if not isinstance(v, list):
            raise ValueError("Blockers must be a list")
        
        for blocker in v:
            if not isinstance(blocker, dict):
                raise ValueError("Each blocker must be a dictionary")
            
            # Ensure required fields exist
            required_fields = {'type', 'description'}
            if not required_fields.issubset(blocker.keys()):
                raise ValueError(f"Each blocker must contain fields: {required_fields}")
        
        return v
    
    @field_validator('estimated_cost', 'actual_cost')
    @classmethod
    def validate_costs(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate cost values are non-negative."""
        if v is not None and v < 0:
            raise ValueError("Costs cannot be negative")
        return v
    
    @model_validator(mode='after')
    def validate_task_constraints(self) -> 'Task':
        """Validate task-level constraints."""
        # Prevent self-referential parent task
        if self.parent_task_id is not None and self.id is not None:
            if self.parent_task_id == self.id:
                raise ValueError("Task cannot be its own parent")
        
        # Validate completion timestamp logic
        if self.completed_at is not None and self.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            raise ValueError("Completed timestamp can only be set for completed or failed tasks")
        
        return self
    
    def is_blocked(self) -> bool:
        """Check if task is currently blocked."""
        return bool(self.blockers) or self.status == TaskStatus.BLOCKED
    
    def has_unresolved_dependencies(self) -> bool:
        """Check if task has dependencies that are not yet completed."""
        # This would typically involve querying the database for dependency statuses
        # For now, return True if dependencies exist (actual implementation would check status)
        return bool(self.dependencies)
    
    def can_be_assigned(self) -> bool:
        """Check if task is ready for assignment."""
        return (
            self.status == TaskStatus.PENDING and
            not self.is_blocked() and
            not self.has_unresolved_dependencies()
        )
    
    def add_blocker(self, blocker_type: str, description: str, **metadata) -> None:
        """Add a blocker to the task."""
        blocker = {
            'type': blocker_type,
            'description': description,
            'created_at': datetime.utcnow().isoformat(),
            **metadata
        }
        if not self.blockers:
            self.blockers = []
        self.blockers.append(blocker)
        self.updated_at = datetime.utcnow()
    
    def remove_blocker(self, blocker_type: str) -> bool:
        """Remove blockers of a specific type."""
        if not self.blockers:
            return False
        
        original_count = len(self.blockers)
        self.blockers = [b for b in self.blockers if b.get('type') != blocker_type]
        
        if len(self.blockers) < original_count:
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def update_status(self, new_status: TaskStatus) -> None:
        """Update task status with proper timestamp handling."""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        # Set completion timestamp when transitioning to completed/failed
        if new_status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and old_status not in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            self.completed_at = datetime.utcnow()
        
        # Clear completion timestamp when moving away from completed/failed
        elif old_status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and new_status not in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            self.completed_at = None