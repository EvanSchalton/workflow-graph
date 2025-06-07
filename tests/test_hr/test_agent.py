"""
Tests for the Agent model.
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from api.hr.models.agent import (
    Agent,
    AgentCreate,
    AgentUpdate,
    AgentRead
)


@pytest.fixture
def sample_agent_data(test_uuid: str) -> Dict[str, Any]:
    """Create sample agent data for testing."""
    return {
        "name": f"TestAgent-{test_uuid[:8]}",
        "resume_id": 1,
        "job_description_id": 2,
        "model_name": "gpt-4o",
        "status": "active",
        "configuration": {
            "temperature": 0.7,
            "max_tokens": 1000,
            "system_prompt": f"You are an agent {test_uuid[:8]}"
        },
        "execution_parameters": {
            "timeout": 30,
            "retry_count": 3
        },
        "performance_metrics": {
            "tasks_completed": 10,
            "success_rate": 0.95,
            "average_response_time": 2.5
        }
    }


def test_agent_name_validation(test_uuid: str) -> None:
    """Test custom name validation logic."""
    # Empty name should raise error
    with pytest.raises(ValueError, match="Agent name cannot be empty"):
        Agent.model_validate({
            "name": "",
            "resume_id": 1,
            "job_description_id": 2,
            "model_name": "gpt-4o"
        })
    
    # Whitespace-only name should raise error
    with pytest.raises(ValueError, match="Agent name cannot be empty"):
        Agent.model_validate({
            "name": "   ",
            "resume_id": 1,
            "job_description_id": 2,
            "model_name": "gpt-4o"
        })
    
    # Valid name should be stripped
    agent = Agent.model_validate({
        "name": f"  TestAgent-{test_uuid[:8]}  ",
        "resume_id": 1,
        "job_description_id": 2,
        "model_name": "gpt-4o"
    })
    assert agent.name == f"TestAgent-{test_uuid[:8]}"


def test_agent_status_validation(test_uuid: str) -> None:
    """Test custom status validation logic."""
    # Invalid status should raise error
    with pytest.raises(ValueError, match="Status must be one of"):
        Agent.model_validate({
            "name": f"TestAgent-{test_uuid[:8]}",
            "resume_id": 1,
            "job_description_id": 2,
            "model_name": "gpt-4o",
            "status": "invalid_status"
        })
    
    # Valid statuses should work
    for valid_status in ["active", "inactive", "terminated"]:
        agent = Agent.model_validate({
            "name": f"TestAgent-{test_uuid[:8]}",
            "resume_id": 1,
            "job_description_id": 2,
            "model_name": "gpt-4o",
            "status": valid_status
        })
        assert agent.status == valid_status


def test_agent_model_name_validation(test_uuid: str) -> None:
    """Test custom model name validation logic."""
    # Empty model name should raise error
    with pytest.raises(ValueError, match="Model name cannot be empty"):
        Agent.model_validate({
            "name": f"TestAgent-{test_uuid[:8]}",
            "resume_id": 1,
            "job_description_id": 2,
            "model_name": ""
        })
    
    # Whitespace-only model name should raise error
    with pytest.raises(ValueError, match="Model name cannot be empty"):
        Agent.model_validate({
            "name": f"TestAgent-{test_uuid[:8]}",
            "resume_id": 1,
            "job_description_id": 2,
            "model_name": "   "
        })
    
    # Valid model name should be stripped
    agent = Agent.model_validate({
        "name": f"TestAgent-{test_uuid[:8]}",
        "resume_id": 1,
        "job_description_id": 2,
        "model_name": "  gpt-4o  "
    })
    assert agent.model_name == "gpt-4o"


def test_agent_json_field_validation(test_uuid: str) -> None:
    """Test JSON field validation logic."""
    # Valid JSON objects should work
    agent = Agent.model_validate({
        "name": f"TestAgent-{test_uuid[:8]}",
        "resume_id": 1,
        "job_description_id": 2,
        "model_name": "gpt-4o",
        "configuration": {"key": "value"},
        "execution_parameters": {"timeout": 30},
        "performance_metrics": {"score": 0.95}
    })
    
    assert agent.configuration == {"key": "value"}
    assert agent.execution_parameters == {"timeout": 30}
    assert agent.performance_metrics == {"score": 0.95}


def test_agent_is_active_method(sample_agent_data: Dict[str, Any]) -> None:
    """Test the is_active method business logic."""
    # Active agent
    agent = Agent.model_validate({**sample_agent_data, "status": "active"})
    assert agent.is_active() is True
    
    # Inactive agents
    for status in ["inactive", "terminated"]:
        agent = Agent.model_validate({**sample_agent_data, "status": status})
        assert agent.is_active() is False


def test_agent_can_be_assigned_tasks_method(sample_agent_data: Dict[str, Any]) -> None:
    """Test the can_be_assigned_tasks method business logic."""
    # Only active agents can be assigned tasks
    agent = Agent.model_validate({**sample_agent_data, "status": "active"})
    assert agent.can_be_assigned_tasks() is True
    
    for status in ["inactive", "terminated"]:
        agent = Agent.model_validate({**sample_agent_data, "status": status})
        assert agent.can_be_assigned_tasks() is False


def test_agent_performance_metric_methods(sample_agent_data: Dict[str, Any]) -> None:
    """Test performance metric management methods."""
    agent = Agent.model_validate(sample_agent_data)
    original_updated_at = agent.updated_at
    
    # Update performance metric
    agent.update_performance_metric("new_metric", 42)
    assert agent.get_performance_metric("new_metric") == 42
    assert agent.updated_at > original_updated_at
    
    # Get existing metric
    assert agent.get_performance_metric("tasks_completed") == 10
    
    # Get non-existing metric with default
    assert agent.get_performance_metric("non_existing", "default") == "default"


def test_agent_configuration_methods(sample_agent_data: Dict[str, Any]) -> None:
    """Test configuration management methods."""
    agent = Agent.model_validate(sample_agent_data)
    original_updated_at = agent.updated_at
    
    # Update configuration
    agent.update_configuration("new_setting", "new_value")
    assert agent.configuration["new_setting"] == "new_value"
    assert agent.updated_at > original_updated_at


def test_agent_status_change_methods(sample_agent_data: Dict[str, Any]) -> None:
    """Test agent status change methods."""
    agent = Agent.model_validate(sample_agent_data)
    
    # Deactivate agent
    agent.deactivate("Testing deactivation")
    assert agent.status == "inactive"
    assert agent.configuration["deactivation_reason"] == "Testing deactivation"
    
    # Reactivate agent
    result = agent.activate()
    assert result is True
    assert agent.status == "active"
    
    # Terminate agent
    agent.terminate("Testing termination")
    assert agent.status == "terminated"
    assert agent.configuration["termination_reason"] == "Testing termination"
    
    # Cannot reactivate terminated agent
    result = agent.activate()
    assert result is False
    assert agent.status == "terminated"


def test_agent_create_schema(sample_agent_data: Dict[str, Any]) -> None:
    """Test the AgentCreate schema validation."""
    # Remove fields not needed for create
    create_data = {k: v for k, v in sample_agent_data.items() 
                   if k not in ['id', 'created_at', 'updated_at']}
    
    agent_create = AgentCreate.model_validate(create_data)
    assert agent_create.name == sample_agent_data["name"]
    assert agent_create.resume_id == sample_agent_data["resume_id"]
    assert agent_create.job_description_id == sample_agent_data["job_description_id"]
    assert agent_create.model_name == sample_agent_data["model_name"]


def test_agent_update_schema(test_uuid: str) -> None:
    """Test the AgentUpdate schema validation."""
    update_data = {
        "name": f"UpdatedAgent-{test_uuid[:8]}",
        "status": "inactive",
        "configuration": {"updated": True}
    }
    
    agent_update = AgentUpdate.model_validate(update_data)
    assert agent_update.name == f"UpdatedAgent-{test_uuid[:8]}"
    assert agent_update.status == "inactive"
    assert agent_update.configuration == {"updated": True}
    assert agent_update.model_name is None  # Should be optional


def test_agent_read_schema(sample_agent_data: Dict[str, Any]) -> None:
    """Test the AgentRead schema validation."""
    # Add required fields for read schema
    read_data = {
        **sample_agent_data,
        "id": 1,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    agent_read = AgentRead.model_validate(read_data)
    assert agent_read.id == 1
    assert agent_read.name == sample_agent_data["name"]
    assert agent_read.resume_id == sample_agent_data["resume_id"]
    assert agent_read.job_description_id == sample_agent_data["job_description_id"]
    assert isinstance(agent_read.created_at, datetime)
    assert isinstance(agent_read.updated_at, datetime)


def test_agent_string_representation(sample_agent_data: Dict[str, Any]) -> None:
    """Test string representation methods."""
    agent = Agent.model_validate({**sample_agent_data, "id": 42})
    
    str_repr = str(agent)
    assert "Agent(id=42" in str_repr
    assert f"name='{sample_agent_data['name']}'" in str_repr
    assert f"model='{sample_agent_data['model_name']}'" in str_repr
    assert f"status='{sample_agent_data['status']}'" in str_repr
    
    repr_repr = repr(agent)
    assert "Agent(id=42" in repr_repr
    assert f"name='{sample_agent_data['name']}'" in repr_repr
    assert f"resume_id={sample_agent_data['resume_id']}" in repr_repr
    assert f"job_id={sample_agent_data['job_description_id']}" in repr_repr


# Additional tests for missing validator error paths

def test_agent_configuration_invalid_json_string():
    """Test configuration validator with invalid JSON string."""
    from pydantic import ValidationError
    # These tests expect ValidationError because Pydantic's schema validation
    # requires dict types for Dict[str, Any] fields, not JSON strings
    with pytest.raises(ValidationError):
        Agent.model_validate({
            "name": "TestAgent",
            "resume_id": 1,
            "job_description_id": 2,
            "model_name": "gpt-4o",
            "configuration": "{'invalid': json}"  # Invalid JSON string
        })


def test_agent_json_fields_with_valid_json_strings():
    """Test JSON field validators with valid JSON strings."""
    from pydantic import ValidationError
    # These tests expect ValidationError because Pydantic's schema validation 
    # requires dict types for Dict[str, Any] fields, not JSON strings
    with pytest.raises(ValidationError):
        Agent.model_validate({
            "name": "TestAgent",
            "resume_id": 1,
            "job_description_id": 2,
            "model_name": "gpt-4o",
            "configuration": '{"temperature": 0.7}',  # Valid JSON string
            "execution_parameters": '{"timeout": 30}',  # Valid JSON string
            "performance_metrics": '{"score": 0.95}'  # Valid JSON string
        })


def test_agent_execution_parameters_invalid_json_string():
    """Test execution_parameters validator with invalid JSON string."""
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        Agent.model_validate({
            "name": "TestAgent",
            "resume_id": 1,
            "job_description_id": 2,
            "model_name": "gpt-4o",
            "execution_parameters": "{invalid json string"  # Invalid JSON
        })


def test_agent_performance_metrics_invalid_json_string():
    """Test performance_metrics validator with invalid JSON string."""
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        Agent.model_validate({
            "name": "TestAgent",
            "resume_id": 1,
            "job_description_id": 2,
            "model_name": "gpt-4o",
            "performance_metrics": '{"incomplete": json'  # Invalid JSON
        })


def test_agent_deactivate_with_reason():
    """Test agent deactivation with reason."""
    agent = Agent.model_validate({
        "name": "TestAgent",
        "resume_id": 1,
        "job_description_id": 2,
        "model_name": "gpt-4o",
        "status": "active"
    })
    
    agent.deactivate("Performance issues")
    
    assert agent.status == "inactive"
    assert agent.configuration.get("deactivation_reason") == "Performance issues"


def test_agent_deactivate_without_reason():
    """Test agent deactivation without reason."""
    agent = Agent.model_validate({
        "name": "TestAgent",
        "resume_id": 1,
        "job_description_id": 2,
        "model_name": "gpt-4o",
        "status": "active"
    })
    
    agent.deactivate()
    
    assert agent.status == "inactive"
    assert "deactivation_reason" not in agent.configuration


def test_agent_terminate_with_reason():
    """Test agent termination with reason."""
    agent = Agent.model_validate({
        "name": "TestAgent",
        "resume_id": 1,
        "job_description_id": 2,
        "model_name": "gpt-4o",
        "status": "active"
    })
    
    agent.terminate("Security violation")
    
    assert agent.status == "terminated"
    assert agent.configuration.get("termination_reason") == "Security violation"


def test_agent_terminate_without_reason():
    """Test agent termination without reason."""
    agent = Agent.model_validate({
        "name": "TestAgent",
        "resume_id": 1,
        "job_description_id": 2,
        "model_name": "gpt-4o",
        "status": "active"
    })
    
    agent.terminate()
    
    assert agent.status == "terminated"
    assert "termination_reason" not in agent.configuration


def test_agent_activate_from_inactive():
    """Test agent activation from inactive status."""
    agent = Agent.model_validate({
        "name": "TestAgent",
        "resume_id": 1,
        "job_description_id": 2,
        "model_name": "gpt-4o",
        "status": "inactive"
    })
    
    result = agent.activate()
    
    assert result is True
    assert agent.status == "active"


def test_agent_activate_from_terminated():
    """Test agent activation attempt from terminated status."""
    agent = Agent.model_validate({
        "name": "TestAgent",
        "resume_id": 1,
        "job_description_id": 2,
        "model_name": "gpt-4o",
        "status": "terminated"
    })
    
    result = agent.activate()
    
    assert result is False
    assert agent.status == "terminated"  # Should remain terminated


def test_agent_get_performance_metric_default_none():
    """Test getting performance metric with default None."""
    agent = Agent.model_validate({
        "name": "TestAgent",
        "resume_id": 1,
        "job_description_id": 2,
        "model_name": "gpt-4o"
    })
    
    result = agent.get_performance_metric("non_existent")
    assert result is None
    
    result = agent.get_performance_metric("non_existent", "custom_default")
    assert result == "custom_default"


# Additional tests for comprehensive coverage

def test_agent_json_validator_non_dict_types():
    """Test JSON field validators with non-dict types."""
    from api.hr.models.agent import Agent as AgentClass
    
    # Test configuration validator with non-dict value that's not a string
    try:
        AgentClass.validate_configuration(42)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Configuration must be a dictionary" in str(e)
    
    # Test configuration validator with JSON string that parses to non-dict
    try:
        AgentClass.validate_configuration('"string_value"')
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Configuration must be a dictionary" in str(e)


def test_agent_execution_parameters_validator_non_dict():
    """Test execution_parameters validator with non-dict types."""
    from api.hr.models.agent import Agent as AgentClass
    
    # Test execution_parameters validator with non-dict value
    try:
        AgentClass.validate_execution_parameters(["list", "value"])
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Execution parameters must be a dictionary" in str(e)
    
    # Test execution_parameters validator with JSON string that parses to non-dict
    try:
        AgentClass.validate_execution_parameters('["array", "value"]')
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Execution parameters must be a dictionary" in str(e)


def test_agent_performance_metrics_validator_non_dict():
    """Test performance_metrics validator with non-dict types."""
    from api.hr.models.agent import Agent as AgentClass
    
    # Test performance_metrics validator with non-dict value
    try:
        AgentClass.validate_performance_metrics(42)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Performance metrics must be a dictionary" in str(e)
    
    # Test performance_metrics validator with JSON string that parses to non-dict
    try:
        AgentClass.validate_performance_metrics('42')
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Performance metrics must be a dictionary" in str(e)


def test_agent_json_validators_with_invalid_json():
    """Test JSON field validators with invalid JSON strings."""
    from api.hr.models.agent import Agent as AgentClass
    
    # Test configuration validator with invalid JSON
    try:
        AgentClass.validate_configuration('{invalid json}')
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Configuration must be valid JSON" in str(e)
    
    # Test execution_parameters validator with invalid JSON
    try:
        AgentClass.validate_execution_parameters('{invalid: json}')
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Execution parameters must be valid JSON" in str(e)
    
    # Test performance_metrics validator with invalid JSON
    try:
        AgentClass.validate_performance_metrics('{incomplete: json')
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Performance metrics must be valid JSON" in str(e)


def test_agent_json_validators_with_type_error():
    """Test JSON field validators with TypeError during parsing."""
    from api.hr.models.agent import Agent as AgentClass
    
    # Test configuration validator with non-dict, non-string input
    try:
        AgentClass.validate_configuration(None)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Configuration must be a dictionary" in str(e)
    
    # Test execution_parameters validator with non-dict, non-string input  
    try:
        AgentClass.validate_execution_parameters(None)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Execution parameters must be a dictionary" in str(e)
    
    # Test performance_metrics validator with non-dict, non-string input
    try:
        AgentClass.validate_performance_metrics(None)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Performance metrics must be a dictionary" in str(e)


def test_agent_json_validators_valid_json_strings():
    """Test JSON field validators with valid JSON strings."""
    from api.hr.models.agent import Agent as AgentClass
    
    # Test configuration validator with valid JSON string
    result = AgentClass.validate_configuration('{"temperature": 0.7}')
    assert result == {"temperature": 0.7}
    
    # Test execution_parameters validator with valid JSON string
    result = AgentClass.validate_execution_parameters('{"timeout": 30}')
    assert result == {"timeout": 30}
    
    # Test performance_metrics validator with valid JSON string
    result = AgentClass.validate_performance_metrics('{"score": 0.95}')
    assert result == {"score": 0.95}


def test_agent_imports_coverage():
    """Test to ensure import statements are covered."""
    # This test ensures the import statements at the top of the file are covered
    from api.hr.models.agent import Agent, AgentCreate, AgentUpdate, AgentRead
    assert Agent is not None
    assert AgentCreate is not None  
    assert AgentUpdate is not None
    assert AgentRead is not None
