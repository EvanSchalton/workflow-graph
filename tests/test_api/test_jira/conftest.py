"""Fixtures for JIRA API tests."""

import pytest
import os
import uuid
from fastapi.testclient import TestClient
from typing import Generator
from api.jira.main import app


@pytest.fixture(scope="function")
def test_uuid() -> str:
    """Generate a unique UUID for testing."""
    return str(uuid.uuid4())


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """Create test client for JIRA API tests using the main app with proper lifespan."""
    # Set test environment to use the 'test' schema
    os.environ["DATABASE_SCHEMA"] = "test"
    
    # Import models to ensure tables are defined
    from api.jira.models.board import Board
    from api.jira.models.status_column import StatusColumn  
    from api.jira.models.ticket import Ticket
    from api.jira.models.ticket_comment import TicketComment
    from api.jira.models.webhook import Webhook
    
    with TestClient(app) as c:
        yield c
