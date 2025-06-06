"""
ModelCatalog model for cost tracking service.
Represents AI models with their costs, capabilities, and performance characteristics.
"""

from typing import List, Optional, Any, TYPE_CHECKING, Union
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import field_validator, model_validator
import enum

if TYPE_CHECKING:
    pass


class PerformanceTier(str, enum.Enum):
    """Valid performance tiers for AI models."""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class ModelCatalog(SQLModel, table=True):
    """
    Model catalog for tracking AI models and their characteristics.
    
    This model maintains information about available AI models including
    their costs per token, context limits, performance tiers, and capabilities.
    Used for cost calculation and model selection decisions.
    """
    __tablename__ = "model_catalog"
    
    # Primary identification
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True, description="Unique model identifier")
    provider: str = Field(max_length=50, description="Model provider (e.g., 'openai', 'anthropic')")
    
    # Cost structure
    cost_per_input_token: Decimal = Field(
        description="Cost per input token in USD",
        decimal_places=8,
        max_digits=10
    )
    cost_per_output_token: Decimal = Field(
        description="Cost per output token in USD", 
        decimal_places=8,
        max_digits=10
    )
    
    # Model capabilities and limits
    context_limit: int = Field(description="Maximum context window size in tokens")
    performance_tier: PerformanceTier = Field(description="Performance classification of the model")
    capabilities: Union[List[str], Any] = Field(
        default_factory=list,
        description="List of model capabilities (e.g., 'coding', 'reasoning', 'image-generation')",
        sa_column=Column(JSONB)
    )
    
    # Status and metadata
    is_active: bool = Field(default=True, description="Whether this model is available for use")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the model was added")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    # Relationships
    # Note: No direct relationship to ExecutionCost since it references by model_name string
    # ExecutionCost records can reference models that may not be in the catalog
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate model name format."""
        if not v or not v.strip():
            raise ValueError("Model name cannot be empty")
        stripped_name = v.strip()
        if len(stripped_name) < 2:
            raise ValueError("Model name must be at least 2 characters")
        return stripped_name
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate provider name format."""
        if not v or not v.strip():
            raise ValueError("Provider name cannot be empty")
        return v.strip().lower()
    
    @field_validator('capabilities', mode='before')
    @classmethod
    def validate_capabilities_before(cls, v) -> List[str]:
        """Pre-validate capabilities to provide custom error messages."""
        if not isinstance(v, list):
            raise ValueError("Capabilities must be a list")
        
        # Check each item is a string
        for i, capability in enumerate(v):
            if not isinstance(capability, str):
                raise ValueError("All capabilities must be strings")
        
        return v
    
    @field_validator('capabilities')
    @classmethod
    def validate_capabilities(cls, v: List[str]) -> List[str]:
        """Validate and normalize capabilities list."""
        # Remove duplicates and normalize
        normalized = []
        seen = set()
        for capability in v:
            normalized_cap = capability.strip().lower()
            if not normalized_cap:
                continue  # Skip empty capabilities
            
            if normalized_cap not in seen:
                normalized.append(normalized_cap)
                seen.add(normalized_cap)
        
        return normalized
    
    @model_validator(mode='after')
    def validate_cost_structure(self) -> 'ModelCatalog':
        """Validate that cost structure makes sense."""
        if self.cost_per_input_token <= 0:
            raise ValueError("Input token cost must be positive")
        if self.cost_per_output_token <= 0:
            raise ValueError("Output token cost must be positive")
        if self.context_limit <= 0:
            raise ValueError("Context limit must be positive")
        
        # Output tokens are typically more expensive than input tokens
        if self.cost_per_output_token < self.cost_per_input_token:
            # This is unusual but not necessarily wrong, so just ensure it's intentional
            pass
        
        return self
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        """
        Calculate total cost for a given number of input and output tokens.
        
        Args:
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
            
        Returns:
            Total cost in USD as Decimal
            
        Raises:
            ValueError: If token counts are negative
        """
        if input_tokens < 0:
            raise ValueError("Input tokens cannot be negative")
        if output_tokens < 0:
            raise ValueError("Output tokens cannot be negative")
        
        input_cost = Decimal(str(input_tokens)) * self.cost_per_input_token
        output_cost = Decimal(str(output_tokens)) * self.cost_per_output_token
        
        return input_cost + output_cost
    
    def has_capability(self, capability: str) -> bool:
        """
        Check if the model has a specific capability.
        
        Args:
            capability: Capability to check for (case-insensitive)
            
        Returns:
            True if the model has the capability, False otherwise
        """
        return capability.strip().lower() in self.capabilities
    
    def get_cost_efficiency_score(self) -> Decimal:
        """
        Calculate a cost efficiency score based on performance tier and costs.
        Lower scores indicate better cost efficiency.
        
        Returns:
            Cost efficiency score (lower is better)
        """
        # Base cost calculation (average of input and output costs per token)
        avg_cost_per_token = (self.cost_per_input_token + self.cost_per_output_token) / 2
        
        # Performance tier multipliers (higher performance = lower efficiency score)
        tier_multipliers = {
            PerformanceTier.BASIC: Decimal('1.0'),      # No adjustment for basic
            PerformanceTier.STANDARD: Decimal('0.8'),   # 20% better efficiency
            PerformanceTier.PREMIUM: Decimal('0.6'),    # 40% better efficiency
            PerformanceTier.ENTERPRISE: Decimal('0.4')  # 60% better efficiency
        }
        
        multiplier = tier_multipliers.get(self.performance_tier, Decimal('1.0'))
        return avg_cost_per_token * multiplier
    
    model_config = {  # type: ignore
        # Note: json_encoders is deprecated, use custom serializers instead
        # For now, removed to eliminate deprecation warnings
        "arbitrary_types_allowed": True,
        "from_attributes": True
    }
        
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (f"ModelCatalog(id={self.id}, name='{self.name}', "
                f"provider='{self.provider}', tier='{self.performance_tier.value}', "
                f"active={self.is_active})")
