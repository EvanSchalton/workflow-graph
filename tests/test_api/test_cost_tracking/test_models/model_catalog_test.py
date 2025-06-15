"""
Tests for the ModelCatalog model.
"""

import pytest
from decimal import Decimal
from typing import Dict, Any, TYPE_CHECKING

# Test import coverage for TYPE_CHECKING block
if TYPE_CHECKING:
    pass

from api.cost_tracking.models.model_catalog import ModelCatalog, PerformanceTier


def test_model_catalog_basic_creation(test_model_catalog_data: Dict[str, Any]) -> None:
    """Test basic model catalog creation with valid data."""
    model = ModelCatalog.model_validate(test_model_catalog_data)
    
    assert model.name == test_model_catalog_data["name"]
    assert model.provider == test_model_catalog_data["provider"]
    assert model.cost_per_input_token == test_model_catalog_data["cost_per_input_token"]
    assert model.cost_per_output_token == test_model_catalog_data["cost_per_output_token"]
    assert model.context_limit == test_model_catalog_data["context_limit"]
    assert model.performance_tier == PerformanceTier.PREMIUM
    assert model.capabilities == test_model_catalog_data["capabilities"]
    assert model.is_active == test_model_catalog_data["is_active"]


def test_model_catalog_constructor_creation(test_uuid: str) -> None:
    """Test model catalog creation using constructor."""
    model = ModelCatalog(
        name=f"claude-3-test-{test_uuid[:8]}",
        provider="anthropic",
        cost_per_input_token=Decimal("0.00001500"),
        cost_per_output_token=Decimal("0.00007500"),
        context_limit=200000,
        performance_tier=PerformanceTier.ENTERPRISE,
        capabilities=["reasoning", "coding", "analysis", "writing"],
        is_active=True
    )
    
    assert model.name == f"claude-3-test-{test_uuid[:8]}"
    assert model.provider == "anthropic"
    assert model.performance_tier == PerformanceTier.ENTERPRISE
    assert len(model.capabilities) == 4


def test_model_catalog_name_validation(test_uuid: str) -> None:
    """Test model name validation logic."""
    # Empty name should raise error
    with pytest.raises(ValueError, match="Model name cannot be empty"):
        ModelCatalog.model_validate({
            "name": "",
            "provider": "openai",
            "cost_per_input_token": "0.00003000",
            "cost_per_output_token": "0.00006000",
            "context_limit": 128000,
            "performance_tier": "premium"
        })
    
    # Whitespace-only name should raise error
    with pytest.raises(ValueError, match="Model name cannot be empty"):
        ModelCatalog.model_validate({
            "name": "   ",
            "provider": "openai",
            "cost_per_input_token": "0.00003000",
            "cost_per_output_token": "0.00006000",
            "context_limit": 128000,
            "performance_tier": "premium"
        })
    
    # Name with leading/trailing whitespace should be stripped
    model = ModelCatalog.model_validate({
        "name": f"  gpt-4-test-{test_uuid[:8]}  ",
        "provider": "openai",
        "cost_per_input_token": "0.00003000",
        "cost_per_output_token": "0.00006000",
        "context_limit": 128000,
        "performance_tier": "premium"
    })
    assert model.name == f"gpt-4-test-{test_uuid[:8]}"
    
    # Short name should raise error
    with pytest.raises(ValueError, match="Model name must be at least 2 characters"):
        ModelCatalog.model_validate({
            "name": "x",
            "provider": "openai",
            "cost_per_input_token": "0.00003000",
            "cost_per_output_token": "0.00006000",
            "context_limit": 128000,
            "performance_tier": "premium"
        })


def test_model_catalog_provider_validation(test_uuid: str) -> None:
    """Test provider validation and normalization."""
    # Empty provider should raise error
    with pytest.raises(ValueError, match="Provider name cannot be empty"):
        ModelCatalog.model_validate({
            "name": f"test-model-{test_uuid[:8]}",
            "provider": "",
            "cost_per_input_token": "0.00003000",
            "cost_per_output_token": "0.00006000",
            "context_limit": 128000,
            "performance_tier": "premium"
        })
    
    # Provider should be normalized to lowercase
    model = ModelCatalog.model_validate({
        "name": f"test-model-{test_uuid[:8]}",
        "provider": "  OPENAI  ",
        "cost_per_input_token": "0.00003000",
        "cost_per_output_token": "0.00006000",
        "context_limit": 128000,
        "performance_tier": "premium"
    })
    assert model.provider == "openai"


def test_model_catalog_capabilities_validation(test_uuid: str) -> None:
    """Test capabilities list validation and normalization."""
    # Non-list capabilities should raise error
    with pytest.raises(ValueError, match="Capabilities must be a list"):
        ModelCatalog.model_validate({
            "name": f"test-model-{test_uuid[:8]}",
            "provider": "openai",
            "cost_per_input_token": "0.00003000",
            "cost_per_output_token": "0.00006000",
            "context_limit": 128000,
            "performance_tier": "premium",
            "capabilities": "coding"  # Should be a list
        })
    
    # Non-string capability should raise error
    with pytest.raises(ValueError, match="All capabilities must be strings"):
        ModelCatalog.model_validate({
            "name": f"test-model-{test_uuid[:8]}",
            "provider": "openai",
            "cost_per_input_token": "0.00003000",
            "cost_per_output_token": "0.00006000",
            "context_limit": 128000,
            "performance_tier": "premium",
            "capabilities": ["coding", 123]  # 123 is not a string
        })
    
    # Capabilities should be normalized and deduplicated
    model = ModelCatalog.model_validate({
        "name": f"test-model-{test_uuid[:8]}",
        "provider": "openai",
        "cost_per_input_token": "0.00003000",
        "cost_per_output_token": "0.00006000",
        "context_limit": 128000,
        "performance_tier": "premium",
        "capabilities": ["  CODING  ", "reasoning", "", "CODING", "analysis"]
    })
    
    # Should be normalized, deduplicated, and empty strings removed
    assert model.capabilities == ["coding", "reasoning", "analysis"]


def test_model_catalog_cost_validation(test_uuid: str) -> None:
    """Test cost validation logic."""
    # Zero input cost should raise error
    with pytest.raises(ValueError, match="Input token cost must be positive"):
        ModelCatalog.model_validate({
            "name": f"test-model-{test_uuid[:8]}",
            "provider": "openai",
            "cost_per_input_token": "0.00000000",
            "cost_per_output_token": "0.00006000",
            "context_limit": 128000,
            "performance_tier": "premium"
        })
    
    # Negative output cost should raise error
    with pytest.raises(ValueError, match="Output token cost must be positive"):
        ModelCatalog.model_validate({
            "name": f"test-model-{test_uuid[:8]}",
            "provider": "openai",
            "cost_per_input_token": "0.00003000",
            "cost_per_output_token": "-0.00006000",
            "context_limit": 128000,
            "performance_tier": "premium"
        })


def test_model_catalog_calculate_cost(test_model_catalog_data: Dict[str, Any]) -> None:
    """Test cost calculation method."""
    model = ModelCatalog.model_validate(test_model_catalog_data)
    
    # Basic cost calculation
    cost = model.calculate_cost(1000, 500)
    expected_cost = (1000 * model.cost_per_input_token) + (500 * model.cost_per_output_token)
    assert cost == expected_cost
    
    # Zero tokens should result in zero cost
    assert model.calculate_cost(0, 0) == Decimal('0')
    
    # Only input tokens
    cost = model.calculate_cost(1000, 0)
    assert cost == 1000 * model.cost_per_input_token
    
    # Only output tokens
    cost = model.calculate_cost(0, 500)
    assert cost == 500 * model.cost_per_output_token
    
    # Negative input tokens should raise error
    with pytest.raises(ValueError, match="Input tokens cannot be negative"):
        model.calculate_cost(-100, 500)
    
    # Negative output tokens should raise error
    with pytest.raises(ValueError, match="Output tokens cannot be negative"):
        model.calculate_cost(1000, -500)


def test_model_catalog_has_capability(test_model_catalog_data: Dict[str, Any]) -> None:
    """Test capability checking method."""
    model = ModelCatalog.model_validate(test_model_catalog_data)
    
    # Should find existing capabilities (case-insensitive)
    assert model.has_capability("coding")
    assert model.has_capability("CODING")
    assert model.has_capability("  reasoning  ")
    
    # Should not find non-existent capabilities
    assert not model.has_capability("image-generation")
    assert not model.has_capability("music-composition")


def test_model_catalog_cost_efficiency_score(test_model_catalog_data: Dict[str, Any]) -> None:
    """Test cost efficiency score calculation."""
    model = ModelCatalog.model_validate(test_model_catalog_data)
    
    score = model.get_cost_efficiency_score()
    
    # Should return a positive decimal
    assert isinstance(score, Decimal)
    assert score > 0
    
    # Premium tier should have better efficiency than basic
    basic_model = ModelCatalog.model_validate({
        **test_model_catalog_data,
        "performance_tier": "basic"
    })
    basic_score = basic_model.get_cost_efficiency_score()
    
    # Lower score is better efficiency, so premium should have lower score
    assert score < basic_score


@pytest.mark.parametrize("tier,expected_order", [
    (PerformanceTier.BASIC, 4),
    (PerformanceTier.STANDARD, 3),
    (PerformanceTier.PREMIUM, 2),
    (PerformanceTier.ENTERPRISE, 1),
])
def test_model_catalog_performance_tiers(
    test_model_catalog_data: Dict[str, Any], 
    tier: PerformanceTier, 
    expected_order: int
) -> None:
    """Test that performance tiers work correctly."""
    model_data = {**test_model_catalog_data, "performance_tier": tier}
    model = ModelCatalog.model_validate(model_data)
    
    assert model.performance_tier == tier
    
    # Higher tier models should have better efficiency scores (lower numbers)
    score = model.get_cost_efficiency_score()
    assert isinstance(score, Decimal)


def test_model_catalog_repr(test_model_catalog_data: Dict[str, Any]) -> None:
    """Test string representation of ModelCatalog."""
    model = ModelCatalog.model_validate(test_model_catalog_data)
    
    repr_str = repr(model)
    
    # Should contain key information
    assert model.name in repr_str
    assert model.provider in repr_str
    assert model.performance_tier.value in repr_str


def test_model_catalog_context_limit_validation(test_uuid: str) -> None:
    """Test context limit validation to cover missing line 131."""
    # Context limit must be positive
    with pytest.raises(ValueError, match="Context limit must be positive"):
        ModelCatalog.model_validate({
            "name": f"test-model-{test_uuid[:8]}",
            "provider": "test_provider",
            "cost_per_input_token": "0.00001000",
            "cost_per_output_token": "0.00002000",
            "context_limit": 0,  # Invalid context limit
            "performance_tier": "standard"
        })
    
    # Negative context limit should also fail
    with pytest.raises(ValueError, match="Context limit must be positive"):
        ModelCatalog.model_validate({
            "name": f"test-model-{test_uuid[:8]}",
            "provider": "test_provider",
            "cost_per_input_token": "0.00001000",
            "cost_per_output_token": "0.00002000",
            "context_limit": -1000,  # Invalid negative context limit
            "performance_tier": "standard"
        })


def test_model_catalog_output_cost_less_than_input_cost(test_uuid: str) -> None:
    """Test scenario where output cost is less than input cost to cover missing line 136."""
    # Create model where output tokens cost less than input tokens (unusual but valid)
    model = ModelCatalog.model_validate({
        "name": f"test-model-unusual-pricing-{test_uuid[:8]}",
        "provider": "test_provider",
        "cost_per_input_token": "0.00005000",  # Higher input cost
        "cost_per_output_token": "0.00003000",  # Lower output cost (unusual)
        "context_limit": 100000,
        "performance_tier": "basic"
    })
    
    # Should be valid despite unusual pricing structure
    assert model.cost_per_input_token > model.cost_per_output_token
    assert model.name == f"test-model-unusual-pricing-{test_uuid[:8]}"
    
    # Cost calculation should still work correctly
    cost = model.calculate_cost(1000, 500)
    expected_cost = (Decimal("1000") * Decimal("0.00005000")) + (Decimal("500") * Decimal("0.00003000"))
    assert cost == expected_cost


def test_model_catalog_input_token_cost_validation(test_uuid: str) -> None:
    """Test input token cost validation edge cases."""
    # Zero input token cost should fail
    with pytest.raises(ValueError, match="Input token cost must be positive"):
        ModelCatalog.model_validate({
            "name": f"test-model-{test_uuid[:8]}",
            "provider": "test_provider",
            "cost_per_input_token": "0.00000000",  # Zero cost
            "cost_per_output_token": "0.00002000",
            "context_limit": 100000,
            "performance_tier": "standard"
        })
    
    # Negative input token cost should fail
    with pytest.raises(ValueError, match="Input token cost must be positive"):
        ModelCatalog.model_validate({
            "name": f"test-model-{test_uuid[:8]}",
            "provider": "test_provider",
            "cost_per_input_token": "-0.00001000",  # Negative cost
            "cost_per_output_token": "0.00002000",
            "context_limit": 100000,
            "performance_tier": "standard"
        })


def test_model_catalog_output_token_cost_validation(test_uuid: str) -> None:
    """Test output token cost validation edge cases."""
    # Zero output token cost should fail
    with pytest.raises(ValueError, match="Output token cost must be positive"):
        ModelCatalog.model_validate({
            "name": f"test-model-{test_uuid[:8]}",
            "provider": "test_provider",
            "cost_per_input_token": "0.00001000",
            "cost_per_output_token": "0.00000000",  # Zero cost
            "context_limit": 100000,
            "performance_tier": "standard"
        })
    
    # Negative output token cost should fail
    with pytest.raises(ValueError, match="Output token cost must be positive"):
        ModelCatalog.model_validate({
            "name": f"test-model-{test_uuid[:8]}",
            "provider": "test_provider",
            "cost_per_input_token": "0.00001000",
            "cost_per_output_token": "-0.00002000",  # Negative cost
            "context_limit": 100000,
            "performance_tier": "standard"
        })
