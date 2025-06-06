"""
Agent model for workforce management.
Represents synthetic agents with resumes and job assignments.
"""

from typing import Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import field_validator
import json

if TYPE_CHECKING:
    from .job_description import JobDescription
    from .resume import Resume


class Agent(SQLModel, table=True):
    """
    Agent model representing synthetic workforce members.
    
    This model represents AI agents that have been hired for specific roles,
    including their configuration, performance metrics, and execution parameters.
    """
    __tablename__ = "agents"
    
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Required fields
    name: str = Field(max_length=255, description="Agent name/identifier")
    
    # Foreign keys
    resume_id: int = Field(foreign_key="resumes.id", description="Associated resume")
    job_description_id: int = Field(foreign_key="job_descriptions.id", description="Assigned job role")
    
    # Agent configuration
    model_name: str = Field(max_length=100, description="AI model used for this agent")
    status: str = Field(
        default="active",
        max_length=50,
        description="Agent operational status"
    )
    
    # JSON configuration fields
    configuration: Dict[str, Any] = Field(
        default_factory=dict,
        description="Agent configuration parameters",
        sa_column=Column(JSONB)
    )
    execution_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Execution and runtime parameters",
        sa_column=Column(JSONB)
    )
    performance_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Performance tracking and metrics",
        sa_column=Column(JSONB)
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    resume: Optional["Resume"] = Relationship(back_populates="agent")
    job_description: Optional["JobDescription"] = Relationship(back_populates="agents")
    # Note: assignments and execution_costs relationships are defined via foreign keys
    # to avoid circular import issues during SQLAlchemy mapper initialization
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate agent name."""
        if not v or not v.strip():
            raise ValueError("Agent name cannot be empty")
        return v.strip()
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate agent status."""
        valid_statuses = {'active', 'inactive', 'terminated'}
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v
    
    @field_validator('model_name')
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        """Validate model name."""
        if not v or not v.strip():
            raise ValueError("Model name cannot be empty")
        return v.strip()
    
    @field_validator('configuration')
    @classmethod
    def validate_configuration(cls, v) -> Dict[str, Any]:
        """Validate configuration JSON."""
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                raise ValueError("Configuration must be valid JSON")
        
        if not isinstance(v, dict):
            raise ValueError("Configuration must be a dictionary")
        
        return v
    
    @field_validator('execution_parameters')
    @classmethod
    def validate_execution_parameters(cls, v) -> Dict[str, Any]:
        """Validate execution parameters JSON."""
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                raise ValueError("Execution parameters must be valid JSON")
        
        if not isinstance(v, dict):
            raise ValueError("Execution parameters must be a dictionary")
        
        return v
    
    @field_validator('performance_metrics')
    @classmethod
    def validate_performance_metrics(cls, v) -> Dict[str, Any]:
        """Validate performance metrics JSON."""
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                raise ValueError("Performance metrics must be valid JSON")
        
        if not isinstance(v, dict):
            raise ValueError("Performance metrics must be a dictionary")
        
        return v
    
    def __str__(self) -> str:
        """String representation of agent."""
        return f"Agent(id={self.id}, name='{self.name}', model='{self.model_name}', status='{self.status}')"
    
    def __repr__(self) -> str:
        """Detailed representation of agent."""
        return (
            f"Agent(id={self.id}, name='{self.name}', "
            f"model='{self.model_name}', status='{self.status}', "
            f"resume_id={self.resume_id}, job_id={self.job_description_id})"
        )
    
    def is_active(self) -> bool:
        """Check if agent is currently active."""
        return self.status == 'active'
    
    def can_be_assigned_tasks(self) -> bool:
        """Check if agent can be assigned new tasks."""
        return self.status == 'active'
    
    def update_performance_metric(self, metric_name: str, value: Any) -> None:
        """Update a specific performance metric."""
        self.performance_metrics[metric_name] = value
        self.updated_at = datetime.utcnow()
    
    def get_performance_metric(self, metric_name: str, default: Any = None) -> Any:
        """Get a specific performance metric."""
        return self.performance_metrics.get(metric_name, default)
    
    def update_configuration(self, key: str, value: Any) -> None:
        """Update a specific configuration parameter."""
        self.configuration[key] = value
        self.updated_at = datetime.utcnow()
    
    def deactivate(self, reason: Optional[str] = None) -> None:
        """Deactivate the agent."""
        self.status = 'inactive'
        self.updated_at = datetime.utcnow()
        if reason:
            self.update_configuration('deactivation_reason', reason)
    
    def terminate(self, reason: Optional[str] = None) -> None:
        """Terminate the agent (permanent)."""
        self.status = 'terminated'
        self.updated_at = datetime.utcnow()
        if reason:
            self.update_configuration('termination_reason', reason)
    
    def activate(self) -> bool:
        """Activate the agent if not terminated."""
        if self.status == 'terminated':
            return False
        
        self.status = 'active'
        self.updated_at = datetime.utcnow()
        return True


class AgentCreate(SQLModel):
    """Schema for creating new agents."""
    name: str = Field(max_length=255)
    resume_id: int
    job_description_id: int
    model_name: str = Field(max_length=100)
    status: str = "active"
    configuration: Dict[str, Any] = Field(default_factory=dict)
    execution_parameters: Dict[str, Any] = Field(default_factory=dict)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)


class AgentUpdate(SQLModel):
    """Schema for updating existing agents."""
    name: Optional[str] = Field(default=None, max_length=255)
    model_name: Optional[str] = Field(default=None, max_length=100)
    status: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    execution_parameters: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None


class AgentRead(SQLModel):
    """Schema for reading agents."""
    id: int
    name: str
    resume_id: int
    job_description_id: int
    model_name: str
    status: str
    configuration: Dict[str, Any]
    execution_parameters: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
