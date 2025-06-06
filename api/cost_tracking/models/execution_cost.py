"""
ExecutionCost model for cost tracking service.
Represents costs incurred from AI model executions by agents on tasks.
"""

from typing import Optional, Dict, Any, TYPE_CHECKING, Union
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import field_validator, model_validator, ConfigDict

if TYPE_CHECKING:
    from .model_catalog import ModelCatalog


class ExecutionCost(SQLModel, table=True):
    """
    Execution cost tracking for AI model usage.
    
    This model tracks the costs incurred when agents execute AI models
    for specific tasks, including token usage, execution time, and 
    consensus round information for cost analysis and optimization.
    """
    __tablename__ = "execution_costs"
    
    # Primary identification
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Foreign key relationships
    agent_id: int = Field(foreign_key="agents.id", description="Agent that executed the model")
    task_id: Optional[int] = Field(
        default=None, 
        foreign_key="tasks.id", 
        description="Task the execution was for (null if not task-related)"
    )
    model_name: str = Field(
        max_length=100, 
        description="Name of the model that was executed"
    )
    
    # Execution details
    execution_type: str = Field(
        max_length=50,
        description="Type of execution (e.g., 'task_completion', 'consensus_vote', 'interview')"
    )
    input_tokens: int = Field(
        default=0, 
        ge=0, 
        description="Number of input tokens used"
    )
    output_tokens: int = Field(
        default=0, 
        ge=0, 
        description="Number of output tokens generated"
    )
    total_cost: Decimal = Field(
        description="Total cost in USD for this execution",
        decimal_places=6,
        max_digits=10,
        ge=0
    )
    
    # Performance and consensus tracking
    execution_time_ms: Optional[int] = Field(
        default=None,
        ge=0,
        description="Execution time in milliseconds (if tracked)"
    )
    consensus_round: int = Field(
        default=1,
        ge=1,
        description="Which consensus round this execution was part of"
    )
    
    # Additional metadata
    execution_metadata: Union[Dict[str, Any], Any] = Field(
        default_factory=dict,
        description="Additional execution metadata",
        sa_column=Column(JSONB)
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, 
        description="When the execution occurred"
    )
    
    # Note: Relationships to Agent and Task models are defined in those models
    # using back_populates. This avoids circular import issues and SQLAlchemy
    # model resolution problems. The relationships can be accessed via:
    # - agent.execution_costs (List[ExecutionCost])  
    # - task.execution_costs (List[ExecutionCost])
    # Individual ExecutionCost records can access related models through
    # queries using agent_id and task_id foreign keys.
    
    # Note: We don't create a direct relationship to ModelCatalog since model_name
    # is just a string reference to allow for models that may not be in catalog
    @property
    def model_catalog_ref(self) -> Optional["ModelCatalog"]:
        """
        Get the model catalog entry for this execution's model.
        This property would be populated by a service layer query.
        """
        # This would be populated by the service layer
        return getattr(self, '_model_catalog_ref', None)
    
    @field_validator('execution_type')
    @classmethod
    def validate_execution_type(cls, v: str) -> str:
        """Validate and normalize execution type."""
        if not v or not v.strip():
            raise ValueError("Execution type cannot be empty")
        
        normalized = v.strip().lower()
        
        # Define valid execution types
        valid_types = {
            'task_completion', 'consensus_vote', 'interview', 'resume_generation', 
            'job_matching', 'performance_evaluation', 'task_decomposition',
            'agent_matching', 'hiring_decision', 'quality_assessment'
        }
        
        if normalized not in valid_types:
            # Allow custom types but warn that they should be documented
            pass
        
        return normalized
    
    @field_validator('model_name')
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        """Validate model name format."""
        if not v or not v.strip():
            raise ValueError("Model name cannot be empty")
        return v.strip()
    
    @field_validator('execution_metadata', mode='before')
    @classmethod
    def validate_metadata_before(cls, v) -> Dict[str, Any]:
        """Pre-validate metadata to provide custom error messages."""
        if not isinstance(v, dict):
            raise ValueError("Execution metadata must be a dictionary")
        
        # Check all keys are strings before proceeding
        for key in v.keys():
            if not isinstance(key, str):
                raise ValueError("All execution metadata keys must be strings")
        
        return v
    
    @field_validator('execution_metadata')
    @classmethod
    def validate_metadata(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metadata structure."""
        # This validator runs after the before validator, so basic checks are done
        return v
    
    @model_validator(mode='after')
    def validate_token_and_cost_consistency(self) -> 'ExecutionCost':
        """Validate that token counts and costs are consistent."""
        # Basic validation that we have either tokens or cost information
        if self.total_cost == 0 and self.input_tokens == 0 and self.output_tokens == 0:
            raise ValueError("Execution must have either token usage or cost information")
        
        # If we have token information, we should have positive cost
        if (self.input_tokens > 0 or self.output_tokens > 0) and self.total_cost <= 0:
            raise ValueError("Executions with token usage must have positive cost")
        
        return self
    
    def get_cost_per_token(self) -> Optional[Decimal]:
        """
        Calculate the effective cost per token for this execution.
        
        Returns:
            Cost per token or None if no tokens were used
        """
        total_tokens = self.input_tokens + self.output_tokens
        if total_tokens == 0:
            return None
        
        return self.total_cost / Decimal(str(total_tokens))
    
    def get_execution_efficiency_score(self) -> Optional[Decimal]:
        """
        Calculate an efficiency score based on cost per token and execution time.
        Lower scores indicate better efficiency.
        
        Returns:
            Efficiency score or None if insufficient data
        """
        cost_per_token = self.get_cost_per_token()
        if cost_per_token is None:
            return None
        
        # Base score is cost per token
        efficiency_score = cost_per_token
        
        # Factor in execution time if available
        if self.execution_time_ms is not None and self.execution_time_ms > 0:
            # Penalize longer execution times (convert ms to seconds for scaling)
            time_penalty = Decimal(str(self.execution_time_ms)) / Decimal('1000') / Decimal('100')
            efficiency_score += time_penalty
        
        return efficiency_score
    
    def is_consensus_execution(self) -> bool:
        """
        Check if this execution was part of a consensus mechanism.
        
        Returns:
            True if this was a consensus execution
        """
        return (self.consensus_round > 1 or 
                self.execution_type in ['consensus_vote', 'hiring_decision'])
    
    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the execution_metadata dictionary with a default.
        
        Args:
            key: Metadata key to retrieve
            default: Default value if key not found
            
        Returns:
            Metadata value or default
        """
        return self.execution_metadata.get(key, default)
    
    def set_metadata_value(self, key: str, value: Any) -> None:
        """
        Set a value in the execution_metadata dictionary.
        
        Args:
            key: Metadata key to set
            value: Value to set
        """
        if not isinstance(key, str):
            raise ValueError("Metadata key must be a string")
        
        # Create a new dict to trigger SQLAlchemy change detection
        new_metadata = dict(self.execution_metadata)
        new_metadata[key] = value
        self.execution_metadata = new_metadata
    
    model_config = ConfigDict(
        # Note: json_encoders is deprecated, use custom serializers instead
        # For now, removed to eliminate deprecation warnings
        arbitrary_types_allowed=True
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (f"ExecutionCost(id={self.id}, agent_id={self.agent_id}, "
                f"task_id={self.task_id}, model='{self.model_name}', "
                f"cost={self.total_cost}, tokens={self.input_tokens + self.output_tokens})")