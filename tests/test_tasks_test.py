"""Tests for tasks module (invoke tasks)."""

import pytest
from unittest.mock import MagicMock, patch
from invoke import Context
import tasks


def test_run_task():
    """Test the run task for starting the FastAPI server."""
    mock_context = MagicMock(spec=Context)
    
    tasks.run(mock_context, port=8080)
    
    mock_context.run.assert_called_once_with(
        "uvicorn api.jira.main:app --reload --port 8080", 
        pty=True
    )


def test_run_task_custom_port():
    """Test the run task with a custom port."""
    mock_context = MagicMock(spec=Context)
    
    tasks.run(mock_context, port=3000)
    
    mock_context.run.assert_called_once_with(
        "uvicorn api.jira.main:app --reload --port 3000", 
        pty=True
    )


def test_test_task_default():
    """Test the test task with default parameters."""
    mock_context = MagicMock(spec=Context)
    
    tasks.test(mock_context)
    
    # Check that run was called with the expected command
    call_args = mock_context.run.call_args[0][0]
    assert "python -m pytest" in call_args
    assert "--cov=api" in call_args
    assert "--cov-branch" in call_args
