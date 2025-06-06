"""
Tests for the ExecutionCost model.
"""

import pytest
from decimal import Decimal
from typing import Dict, Any

from api.cost_tracking.models.execution_cost import ExecutionCost


def test_execution_cost_basic_creation(test_execution_cost_data: Dict[str, Any]) -> None:
    """Test basic execution cost creation with valid data."""
    cost = ExecutionCost.model_validate(test_execution_cost_data)
    
    assert cost.agent_id == test_execution_cost_data["agent_id"]
    assert cost.task_id == test_execution_cost_data["task_id"]
    assert cost.model_name == test_execution_cost_data["model_name"]
    assert cost.execution_type == test_execution_cost_data["execution_type"]
    assert cost.input_tokens == test_execution_cost_data["input_tokens"]
    assert cost.output_tokens == test_execution_cost_data["output_tokens"]
    assert cost.total_cost == test_execution_cost_data["total_cost"]
    assert cost.execution_time_ms == test_execution_cost_data["execution_time_ms"]
    assert cost.consensus_round == test_execution_cost_data["consensus_round"]
    assert cost.execution_metadata == test_execution_cost_data["execution_metadata"]


def test_execution_cost_constructor_creation(test_uuid: str) -> None:
    """Test execution cost creation using constructor."""
    cost = ExecutionCost(
        agent_id=1,
        task_id=None,  # Optional task
        model_name=f"claude-test-{test_uuid[:8]}",
        execution_type="interview",
        input_tokens=800,
        output_tokens=200,
        total_cost=Decimal("0.03000"),
        consensus_round=2,
        execution_metadata={"interview_type": "technical", "test_id": test_uuid}
    )
    
    assert cost.agent_id == 1
    assert cost.task_id is None
    assert cost.model_name == f"claude-test-{test_uuid[:8]}"
    assert cost.execution_type == "interview"
    assert cost.consensus_round == 2


def test_execution_cost_execution_type_validation(test_uuid: str) -> None:
    """Test execution type validation and normalization."""
    # Empty execution type should raise error
    with pytest.raises(ValueError, match="Execution type cannot be empty"):
        ExecutionCost.model_validate({
            "agent_id": 1,
            "model_name": f"test-model-{test_uuid[:8]}",
            "execution_type": "",
            "input_tokens": 100,
            "output_tokens": 50,
            "total_cost": "0.01000"
        })
    
    # Execution type should be normalized to lowercase
    cost = ExecutionCost.model_validate({
        "agent_id": 1,
        "model_name": f"test-model-{test_uuid[:8]}",
        "execution_type": "  TASK_COMPLETION  ",
        "input_tokens": 100,
        "output_tokens": 50,
        "total_cost": "0.01000"
    })
    assert cost.execution_type == "task_completion"


def test_execution_cost_model_name_validation(test_uuid: str) -> None:
    """Test model name validation."""
    # Empty model name should raise error
    with pytest.raises(ValueError, match="Model name cannot be empty"):
        ExecutionCost.model_validate({
            "agent_id": 1,
            "model_name": "",
            "execution_type": "task_completion",
            "input_tokens": 100,
            "output_tokens": 50,
            "total_cost": "0.01000"
        })
    
    # Model name should be stripped
    cost = ExecutionCost.model_validate({
        "agent_id": 1,
        "model_name": f"  test-model-{test_uuid[:8]}  ",
        "execution_type": "task_completion",
        "input_tokens": 100,
        "output_tokens": 50,
        "total_cost": "0.01000"
    })
    assert cost.model_name == f"test-model-{test_uuid[:8]}"


def test_execution_cost_execution_metadata_validation(test_uuid: str) -> None:
    """Test execution metadata validation."""
    # Non-dict metadata should raise error
    with pytest.raises(ValueError, match="Execution metadata must be a dictionary"):
        ExecutionCost.model_validate({
            "agent_id": 1,
            "model_name": f"test-model-{test_uuid[:8]}",
            "execution_type": "task_completion",
            "input_tokens": 100,
            "output_tokens": 50,
            "total_cost": "0.01000",
            "execution_metadata": "not a dict"
        })
    
    # Non-string keys should raise error
    with pytest.raises(ValueError, match="All execution metadata keys must be strings"):
        ExecutionCost.model_validate({
            "agent_id": 1,
            "model_name": f"test-model-{test_uuid[:8]}",
            "execution_type": "task_completion",
            "input_tokens": 100,
            "output_tokens": 50,
            "total_cost": "0.01000",
            "execution_metadata": {123: "value"}  # Key should be string
        })


def test_execution_cost_token_and_cost_consistency(test_uuid: str) -> None:
    """Test token and cost consistency validation."""
    # No tokens and no cost should raise error
    with pytest.raises(ValueError, match="Execution must have either token usage or cost information"):
        ExecutionCost.model_validate({
            "agent_id": 1,
            "model_name": f"test-model-{test_uuid[:8]}",
            "execution_type": "task_completion",
            "input_tokens": 0,
            "output_tokens": 0,
            "total_cost": "0.00000"
        })
    
    # Tokens without cost should raise error
    with pytest.raises(ValueError, match="Executions with token usage must have positive cost"):
        ExecutionCost.model_validate({
            "agent_id": 1,
            "model_name": f"test-model-{test_uuid[:8]}",
            "execution_type": "task_completion",
            "input_tokens": 100,
            "output_tokens": 50,
            "total_cost": "0.00000"
        })
    
    # Valid: Cost without tokens (e.g., flat fee models)
    cost = ExecutionCost.model_validate({
        "agent_id": 1,
        "model_name": f"test-model-{test_uuid[:8]}",
        "execution_type": "task_completion",
        "input_tokens": 0,
        "output_tokens": 0,
        "total_cost": "5.00000"  # Flat fee
    })
    assert cost.total_cost == Decimal("5.00000")


def test_execution_cost_get_cost_per_token(test_execution_cost_data: Dict[str, Any]) -> None:
    """Test cost per token calculation."""
    cost = ExecutionCost.model_validate(test_execution_cost_data)
    
    # Should calculate cost per token correctly
    total_tokens = test_execution_cost_data["input_tokens"] + test_execution_cost_data["output_tokens"]
    expected_cost_per_token = test_execution_cost_data["total_cost"] / Decimal(str(total_tokens))
    
    assert cost.get_cost_per_token() == expected_cost_per_token
    
    # Zero tokens should return None
    zero_token_cost = ExecutionCost.model_validate({
        "agent_id": 1,
        "model_name": "test-model",
        "execution_type": "task_completion",
        "input_tokens": 0,
        "output_tokens": 0,
        "total_cost": "5.00000"  # Flat fee
    })
    assert zero_token_cost.get_cost_per_token() is None


def test_execution_cost_get_execution_efficiency_score(test_execution_cost_data: Dict[str, Any]) -> None:
    """Test execution efficiency score calculation."""
    cost = ExecutionCost.model_validate(test_execution_cost_data)
    
    score = cost.get_execution_efficiency_score()
    
    # Should return a positive decimal that includes cost per token
    assert isinstance(score, Decimal)
    assert score > 0
    
    # Score should be based on cost per token plus time penalty
    cost_per_token = cost.get_cost_per_token()
    assert score > cost_per_token  # Should be higher due to time penalty
    
    # Execution without tokens should return None
    zero_token_cost = ExecutionCost.model_validate({
        "agent_id": 1,
        "model_name": "test-model",
        "execution_type": "task_completion", 
        "input_tokens": 0,
        "output_tokens": 0,
        "total_cost": "5.00000"
    })
    assert zero_token_cost.get_execution_efficiency_score() is None


def test_execution_cost_is_consensus_execution(test_execution_cost_data: Dict[str, Any]) -> None:
    """Test consensus execution detection."""
    # Regular execution (round 1, not consensus type)
    cost = ExecutionCost.model_validate(test_execution_cost_data)
    assert not cost.is_consensus_execution()
    
    # Consensus round > 1
    consensus_cost = ExecutionCost.model_validate({
        **test_execution_cost_data,
        "consensus_round": 3
    })
    assert consensus_cost.is_consensus_execution()
    
    # Consensus execution type
    vote_cost = ExecutionCost.model_validate({
        **test_execution_cost_data,
        "execution_type": "consensus_vote",
        "consensus_round": 1
    })
    assert vote_cost.is_consensus_execution()
    
    # Hiring decision type
    hiring_cost = ExecutionCost.model_validate({
        **test_execution_cost_data,
        "execution_type": "hiring_decision"
    })
    assert hiring_cost.is_consensus_execution()


def test_execution_cost_metadata_helpers(test_execution_cost_data: Dict[str, Any]) -> None:
    """Test metadata helper methods."""
    cost = ExecutionCost.model_validate(test_execution_cost_data)
    
    # Get existing metadata value
    assert cost.get_metadata_value("quality_score") == 0.95
    
    # Get non-existent metadata value with default
    assert cost.get_metadata_value("non_existent", "default") == "default"
    
    # Set metadata value
    cost.set_metadata_value("new_key", "new_value")
    assert cost.get_metadata_value("new_key") == "new_value"
    
    # Set metadata with non-string key should raise error
    with pytest.raises(ValueError, match="Metadata key must be a string"):
        cost.set_metadata_value(123, "value")


@pytest.mark.parametrize("input_tokens,output_tokens,expected_efficiency_order", [
    (1000, 500, 1),  # Standard execution
    (2000, 1000, 2),  # Higher token usage = lower efficiency
    (500, 250, 0),   # Lower token usage = higher efficiency
])
def test_execution_cost_efficiency_comparison(
    test_execution_cost_data: Dict[str, Any],
    input_tokens: int,
    output_tokens: int, 
    expected_efficiency_order: int
) -> None:
    """Test that efficiency scores order correctly."""
    # Create execution cost with different token usage
    cost_data = {
        **test_execution_cost_data,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_cost": Decimal("0.06000")  # Same cost for comparison
    }
    cost = ExecutionCost.model_validate(cost_data)
    
    score = cost.get_execution_efficiency_score()
    assert isinstance(score, Decimal)
    assert score > 0


def test_execution_cost_negative_token_validation(test_uuid: str) -> None:
    """Test that negative token counts are rejected."""
    # Negative input tokens
    with pytest.raises(ValueError):
        ExecutionCost.model_validate({
            "agent_id": 1,
            "model_name": f"test-model-{test_uuid[:8]}",
            "execution_type": "task_completion",
            "input_tokens": -100,
            "output_tokens": 50,
            "total_cost": "0.01000"
        })
    
    # Negative output tokens
    with pytest.raises(ValueError):
        ExecutionCost.model_validate({
            "agent_id": 1,
            "model_name": f"test-model-{test_uuid[:8]}",
            "execution_type": "task_completion",
            "input_tokens": 100,
            "output_tokens": -50,
            "total_cost": "0.01000"
        })


def test_execution_cost_repr(test_execution_cost_data: Dict[str, Any]) -> None:
    """Test string representation of ExecutionCost."""
    cost = ExecutionCost.model_validate(test_execution_cost_data)
    
    repr_str = repr(cost)
    
    # Should contain key information
    assert str(cost.agent_id) in repr_str
    assert str(cost.task_id) in repr_str
    assert cost.model_name in repr_str
    assert str(cost.total_cost) in repr_str
    assert "ExecutionCost" in repr_str
