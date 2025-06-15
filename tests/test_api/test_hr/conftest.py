"""
Test configuration for HR API tests in the new structure.
"""

import pytest
import sys
from pathlib import Path
from uuid import uuid4

# Add the workspace root to the Python path so we can import api modules
workspace_root = Path(__file__).resolve().parent.parent.parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))


@pytest.fixture(scope="function")
def test_uuid() -> str:
    """Generate a unique UUID for testing."""
    return str(uuid4())
