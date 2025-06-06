"""
Test configuration for prompt management tests.
"""

import pytest
import uuid


@pytest.fixture
def test_uuid() -> str:
    """Generate a unique UUID for test traceability."""
    return str(uuid.uuid4())


@pytest.fixture
def task_prompt_data(test_uuid: str) -> dict:
    """Factory fixture for creating test task prompt data."""
    return {
        "name": f"test_task_prompt_{test_uuid[:8]}",
        "description": f"Test task prompt for {test_uuid}",
        "prompt_template": "Execute task: {task_description} with parameters: {parameters}",
        "variables": ["task_description", "parameters"],
        "task_type": "test_execution",
        "version": 1,
        "is_active": True
    }


@pytest.fixture
def resume_prompt_data(test_uuid: str) -> dict:
    """Factory fixture for creating test resume prompt data."""
    return {
        "name": f"test_resume_prompt_{test_uuid[:8]}",
        "description": f"Test resume prompt for {test_uuid}",
        "prompt_template": "Generate a {persona_type} persona with {experience_level} experience in {domain}",
        "variables": ["persona_type", "experience_level", "domain"],
        "persona_type": "analytical",
        "version": 1,
        "is_active": True
    }
