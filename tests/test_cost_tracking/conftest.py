"""
Test configuration for cost tracking tests.
"""

import pytest
import sys
from pathlib import Path
from uuid import uuid4
from decimal import Decimal
from typing import Dict, Any
from datetime import datetime

# Add the workspace root to the Python path so we can import api modules
workspace_root = Path(__file__).resolve().parent.parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))


@pytest.fixture
def test_uuid() -> str:
    """Generate a unique UUID for testing."""
    return str(uuid4())


@pytest.fixture
def test_model_catalog_data(test_uuid: str) -> Dict[str, Any]:
    """Create sample model catalog data for testing."""
    return {
        "name": f"gpt-4-test-{test_uuid[:8]}",
        "provider": "openai",
        "cost_per_input_token": Decimal("0.00003000"),
        "cost_per_output_token": Decimal("0.00006000"),
        "context_limit": 128000,
        "performance_tier": "premium",
        "capabilities": ["coding", "reasoning", "analysis"],
        "is_active": True
    }


@pytest.fixture
def test_execution_cost_data(test_uuid: str) -> Dict[str, Any]:
    """Create sample execution cost data for testing."""
    return {
        "agent_id": 1,
        "task_id": 1,
        "model_name": f"gpt-4-test-{test_uuid[:8]}",
        "execution_type": "task_completion",
        "input_tokens": 1000,
        "output_tokens": 500,
        "total_cost": Decimal("0.06000"),
        "execution_time_ms": 2500,
        "consensus_round": 1,
        "execution_metadata": {"quality_score": 0.95, "test_id": test_uuid}
    }
    return {
        "agent_id": 1,
        "task_id": 1,
        "model_name": f"gpt-4-test-{test_uuid[:8]}",
        "execution_type": "task_completion",
        "input_tokens": 1000,
        "output_tokens": 500,
        "total_cost": Decimal("0.06000"),
        "execution_time_ms": 2500,
        "consensus_round": 1,
        "execution_metadata": {"quality_score": 0.95, "test_id": test_uuid}
    }
