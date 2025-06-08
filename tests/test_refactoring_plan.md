# Test Structure Refactoring Plan

## Current Findings

We've identified that our current tests are structured by feature area (e.g., `boards_test.py`, `tickets_test.py`), but our application code is structured by function (`get_boards.py`, `create_board.py`). According to our development patterns document, we should mirror the application code structure in our test files.

## Test Directory Structure Issue

While attempting to refactor our test files to match the application structure, we encountered several challenges:

1. **Pytest Discovery Issues**: Moving from a flat structure to a nested structure without proper planning can cause import and discovery issues.

2. **Conftest.py Conflicts**: Using `pytest_plugins` in non-top-level conftest files is deprecated and causes test collection errors.

3. **File Naming Conflicts**: Having files with the same basename in different directories can cause import confusion.

## Recommended Approach

Based on our findings, here's a recommended approach to refactor our test directory structure:

### 1. Keep Original Tests Working During Transition

First, keep the original test files (`boards_test.py`, `tickets_test.py`) working during the transition. This ensures we maintain test coverage while refactoring.

### 2. Create New Test Structure with Clear Naming

Create a new test directory structure that mirrors the application code, but use distinct file names to avoid import conflicts:

```
tests/
  test_jira/
    # Original test files (keep during transition)
    boards_test.py 
    tickets_test.py
    columns_test.py
    
    # New structured tests
    routes/
      boards/
        create_board_endpoint_test.py  # Tests for api/jira/routes/boards/create_board.py
        get_boards_endpoint_test.py    # Tests for api/jira/routes/boards/get_boards.py
        get_board_by_id_endpoint_test.py  # Tests for api/jira/routes/boards/get_board_by_id.py
        update_board_endpoint_test.py  # Tests for api/jira/routes/boards/update_board.py
        delete_board_endpoint_test.py  # Tests for api/jira/routes/boards/delete_board_with_events.py
      
      tickets/
        create_ticket_endpoint_test.py  # Tests for api/jira/routes/tickets/create_ticket.py
        ...
```

### 3. Keep Test Files Simple

Each test file should focus on testing a single application code file and include:
- Success cases
- Error cases
- Edge cases

### 4. Extract Test Functions

Extract relevant test functions from existing test files and move them to the new structure:

```python
# Original test in boards_test.py
def test_create_board(client, test_uuid):
    """Test creating a board."""
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    assert board_response.status_code == 200
    
# New test in routes/boards/create_board_endpoint_test.py
def test_create_board_success(client, test_uuid):
    """Test successful board creation."""
    board_data = {"name": f"Test Board {test_uuid}"}
    response = client.post("/api/boards/", json=board_data)
    
    assert response.status_code == 200
    board = response.json()
    assert board["name"] == f"Test Board {test_uuid}"
    assert "id" in board

def test_create_board_validation_error(client):
    """Test board creation with invalid data."""
    # Missing required name field
    response = client.post("/api/boards/", json={})
    assert response.status_code == 422  # Unprocessable Entity
```

### 5. Incremental Testing

After creating each new test file:
1. Run the original test file to ensure base functionality still works
2. Run the new test file to ensure refactored tests work

### 6. Avoid Common Pitfalls

- **No `__init__.py` Files**: Don't add `__init__.py` files in test directories as per our development patterns
- **No Non-Top-Level pytest_plugins**: Don't use `pytest_plugins` in non-top-level `conftest.py` files
- **Use Distinct File Names**: Ensure test file names are unique to avoid import conflicts

### 7. Gradual Phase-Out

Once all functionality is covered by the new test structure, gradually phase out the original test files.

## Example Implementation

Here's a concrete example of how to refactor a test for the `get_boards.py` function:

```python
# filepath: /workspaces/workflow-graph/tests/test_jira/routes/boards/get_boards_endpoint_test.py
"""Tests for the get_boards endpoint."""
import pytest
from fastapi.testclient import TestClient


def test_get_boards_returns_list(client, test_uuid):
    """Test that get_boards returns a list of boards."""
    # Create a test board first
    board_data = {"name": f"Test Board {test_uuid}"}
    create_response = client.post("/api/boards/", json=board_data)
    
    # Get all boards
    get_response = client.get("/api/boards/")
    assert get_response.status_code == 200
    
    # Verify response structure
    boards = get_response.json()
    assert isinstance(boards, list)
    
    # Verify our test board is in the response
    board_id = create_response.json()["id"]
    found = any(b["id"] == board_id for b in boards)
    assert found, f"Board with ID {board_id} not found in boards list"


def test_get_boards_empty_result(client):
    """Test getting boards when none exist (or no matching ones).
    
    This is a limited test because in a shared test environment,
    there might be boards created by other tests.
    """
    response = client.get("/api/boards/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## Next Steps

1. Create a single working test file following this pattern
2. Verify it works alongside existing tests
3. Create a few more test files for different endpoints
4. Once the pattern is proven, complete the refactoring for all endpoints

This approach allows us to incrementally refactor our tests while maintaining test coverage.
