"""
AuditLog model for tracking all system activities.
Provides a comprehensive audit trail for all entity changes and actions.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import field_validator, model_validator
import enum


class EntityType(str, enum.Enum):
    """Valid entity types that can be audited."""
    JOB_DESCRIPTION = "job_description"
    RESUME = "resume"
    JOB_APPLICATION = "job_application"
    AGENT = "agent"
    TASK = "task"
    TASK_ASSIGNMENT = "task_assignment"
    MODEL_CATALOG = "model_catalog"
    EXECUTION_COST = "execution_cost"
    TASK_PROMPT = "task_prompt"
    RESUME_PROMPT = "resume_prompt"


class ActorType(str, enum.Enum):
    """Valid actor types that can perform actions."""
    SYSTEM = "system"
    USER = "user"
    AGENT = "agent"
    API = "api"
    SCHEDULER = "scheduler"
    WEBHOOK = "webhook"


class AuditAction(str, enum.Enum):
    """Valid audit actions."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    READ = "read"
    EXECUTE = "execute"
    ASSIGN = "assign"
    UNASSIGN = "unassign"
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"
    APPROVE = "approve"
    REJECT = "reject"
    COMPLETE = "complete"
    FAIL = "fail"


class AuditLog(SQLModel, table=True):
    """
    Audit log model for tracking all system activities.
    
    This model provides a comprehensive audit trail for all entity changes
    and actions performed in the system, enabling security monitoring,
    compliance reporting, and debugging capabilities.
    """
    __tablename__ = "audit_logs"
    
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Required fields
    entity_type: EntityType = Field(description="Type of entity being audited")
    entity_id: int = Field(description="ID of the entity being audited")
    action: AuditAction = Field(description="Action performed on the entity")
    actor_type: ActorType = Field(description="Type of actor performing the action")
    
    # Optional fields
    actor_id: Optional[int] = Field(default=None, description="ID of the actor performing the action")
    old_values: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Previous values before change",
        sa_column=Column(JSONB)
    )
    new_values: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="New values after change",
        sa_column=Column(JSONB)
    )
    metadata_info: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Additional audit metadata",
        sa_column=Column("metadata", JSONB, nullable=False, default={})
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the audit event occurred")
    
    @field_validator('entity_id', mode='before')
    @classmethod
    def validate_entity_id(cls, v: int) -> int:
        """Validate that entity_id is positive."""
        if v <= 0:
            raise ValueError("entity_id must be positive")
        return v
    
    @field_validator('actor_id', mode='before')
    @classmethod
    def validate_actor_id(cls, v: Optional[int]) -> Optional[int]:
        """Validate that actor_id is positive when provided."""
        if v is not None and v <= 0:
            raise ValueError("actor_id must be positive when provided")
        return v
    
    @field_validator('metadata_info')
    @classmethod
    def validate_metadata_info(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metadata_info is a dictionary."""
        if not isinstance(v, dict):
            raise ValueError("metadata_info must be a dictionary")
        return v
    
    @model_validator(mode='after')
    def validate_model(self) -> 'AuditLog':
        """Validate the complete model after all fields are processed."""
        # Additional validation for entity_id
        if self.entity_id <= 0:
            raise ValueError("entity_id must be positive")
        
        # Additional validation for actor_id
        if self.actor_id is not None and self.actor_id <= 0:
            raise ValueError("actor_id must be positive when provided")
        
        return self
    
    def __str__(self) -> str:
        """String representation of the audit log entry."""
        actor_info = f"{self.actor_type.value}:{self.actor_id}" if self.actor_id else str(self.actor_type.value)
        return f"{self.action.value.upper()} {self.entity_type.value}:{self.entity_id} by {actor_info} at {self.created_at}"
    
    def __repr__(self) -> str:
        """Developer-friendly representation of the audit log entry."""
        return (f"AuditLog(id={self.id}, entity_type='{self.entity_type.value}', "
                f"entity_id={self.entity_id}, action='{self.action.value}', "
                f"actor_type='{self.actor_type.value}', actor_id={self.actor_id})")
