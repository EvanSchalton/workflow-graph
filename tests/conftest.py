import asyncio
import pytest
from uuid import uuid4
from pathlib import Path
import sys
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.jira.main import app

@pytest.fixture
def test_uuid():
    """Generate a unique UUID for testing."""
    return str(uuid4())

@pytest.fixture
def client():
    """Provide a TestClient for testing, ensuring the app's lifespan is started."""
    with TestClient(app) as c:
        # Manually start the app's lifespan
        asyncio.run(app.router.startup())
        try:
            yield c
        finally:
            # Manually stop the app's lifespan
            asyncio.run(app.router.shutdown())