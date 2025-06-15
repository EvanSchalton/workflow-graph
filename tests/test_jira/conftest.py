import os
import sys
import pytest
import pytest_asyncio
from pathlib import Path
from typing import Generator, AsyncGenerator
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.utils import ensure_clean_test_environment

# Add the workspace root to the Python path so we can import api modules
workspace_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(workspace_root))

# Import JIRA modules after adding workspace root to path
from api.jira.main import app  # noqa: E402

@pytest.fixture(scope="function")
def test_uuid() -> str:
    """Generate a unique UUID for testing."""
    return str(uuid4())

@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """Provide a TestClient for testing using the real dev database."""
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


@pytest_asyncio.fixture(scope="function", autouse=True)
async def cleanup_database() -> AsyncGenerator[None, None]:
    """
    Automatically clean up the database before each test to ensure isolation.
    
    This fixture runs before each test function and cleans up any existing
    test data to prevent interference between tests.
    """
    # Import after setting environment
    os.environ["DATABASE_SCHEMA"] = "test"
    
    try:
        from api.jira.database.get_session import get_session_maker
        
        # Get a database session
        session_maker = get_session_maker()
        async with session_maker() as session:
            # Clean up the test schema before running the test
            await ensure_clean_test_environment(session, "test")
            
        yield
        
    except Exception as e:
        # Log the error but don't fail the test setup
        print(f"Warning: Database cleanup failed: {e}")
        yield