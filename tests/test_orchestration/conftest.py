"""
Pytest configuration for orchestration tests.
"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from decimal import Decimal


@pytest.fixture
def test_uuid() -> str:
    """Generate a unique test UUID for traceability."""
    return str(uuid4())


@pytest.fixture
def task_factory(test_uuid: str):
    """Factory for creating test task data."""
    def _factory(
        title: str = None,
        description: str = None,
        jira_task_id: str = None,
        required_skills: list = None,
        **kwargs
    ):
        from api.orchestration.models.task import Task, TaskStatus, TaskPriority
        
        return Task(
            title=title or f"Test Task {test_uuid[:8]}",
            description=description or f"Test task description with UUID {test_uuid}",
            jira_task_id=jira_task_id or f"TEST-{test_uuid[:8]}",
            required_skills=required_skills or ["python", "testing"],
            **kwargs
        )
    return _factory


@pytest.fixture
def assignment_factory(test_uuid: str):
    """Factory for creating test task assignment data."""
    def _factory(
        task_id: int = 1,
        agent_id: int = 1,
        capability_score: Decimal = None,
        **kwargs
    ):
        from api.orchestration.models.task_assignment import TaskAssignment, AssignmentStatus
        
        return TaskAssignment(
            task_id=task_id,
            agent_id=agent_id,
            capability_score=capability_score or Decimal("85.5"),
            **kwargs
        )
    return _factory
