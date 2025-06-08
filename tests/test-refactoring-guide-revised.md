# Test Refactoring Guide

This document provides guidance on how to refactor our test directory structure to align with our application code structure, following the pattern described in `development-patterns.md`.

## Current Test Structure

Currently, we have test files organized by feature area:
- `/tests/test_jira/boards_test.py` - Contains all board-related tests
- `/tests/test_jira/tickets_test.py` - Contains all ticket-related tests
- `/tests/test_jira/columns_test.py` - Contains all column-related tests

## Target Test Structure

We want to mirror the application code structure in our test files:
- For each application file `api/jira/routes/boards/get_boards.py`, we should have a corresponding test file `tests/test_jira/routes/boards/get_boards_test.py`
- This ensures that tests for each function/class are in a separate file that mirrors the application code structure

## Refactoring Approach

### Step 1: Create the Directory Structure
```bash
# Create directory structure for board-related tests
mkdir -p tests/test_jira/routes/boards
mkdir -p tests/test_jira/routes/tickets
mkdir -p tests/test_jira/routes/columns
mkdir -p tests/test_jira/routes/webhooks
```

### Step 2: Identify Test Functions to Move
For each application file, identify corresponding test functions from the existing test files.

For example:
- For `api/jira/routes/boards/get_boards.py`, find all test functions that test this functionality in `tests/test_jira/boards_test.py`
- Ensure you include all test cases for different scenarios (success, error, edge cases)

### Step 3: Create New Test Files
Create a new test file with the same name as the application file, but with `_test.py` suffix.

For example:
- For `api/jira/routes/boards/get_boards.py`, create `tests/test_jira/routes/boards/get_boards_test.py`
- Include all relevant test functions from Step 2

### Step 4: Extend Test Coverage
Since we're breaking down tests by function, ensure that each function has comprehensive test coverage:
- Success case
- Error cases
- Edge cases

### Example: Board Tests

Original test in `tests/test_jira/boards_test.py`:
```python
def test_read_boards(client, test_uuid):
    """Test reading all boards."""
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    response = client.get("/api/boards/")
    assert response.status_code == 200
```

Refactored test in `tests/test_jira/routes/boards/get_boards_test.py`:
```python
def test_get_boards(client, test_uuid):
    """Test retrieving all boards."""
    # Create two test boards
    board1_data = {"name": f"Board One {test_uuid}"}
    board2_data = {"name": f"Board Two {test_uuid}"}
    
    response1 = client.post("/api/boards/", json=board1_data)
    response2 = client.post("/api/boards/", json=board2_data)
    
    board1_id = response1.json()["id"]
    board2_id = response2.json()["id"]
    
    # Get all boards
    get_all_response = client.get("/api/boards/")
    assert get_all_response.status_code == 200
    
    # Find our test boards in the response
    boards = get_all_response.json()
    assert isinstance(boards, list)
    
    # Find board1 in the response
    board1 = next((b for b in boards if b["id"] == board1_id), None)
    assert board1 is not None, f"Board with ID {board1_id} not found in API response"
    assert board1["name"] == f"Board One {test_uuid}"
    
    # Find board2 in the response
    board2 = next((b for b in boards if b["id"] == board2_id), None)  
    assert board2 is not None, f"Board with ID {board2_id} not found in API response"
    assert board2["name"] == f"Board Two {test_uuid}"
```

### Important Notes on Testing Infrastructure

1. **Fixture Availability**
   - Ensure that fixtures like `client` and `test_uuid` are available in your test files
   - These are defined in the top-level `conftest.py` files

2. **Test Naming Convention**
   - Test directories should start with `test_`
   - Test files should end with `_test.py`

3. **No `__init__.py` Files**
   - Do not add `__init__.py` files in test directories as per our development patterns

4. **Running Tests**
   - Run specific test files with: `pytest tests/test_jira/routes/boards/get_boards_test.py`
   - Run all tests for a module with: `pytest tests/test_jira/routes/boards/`

5. **Test Independence**
   - Each test should be independent and not rely on state from other tests
   - Use fixtures for setup/teardown

### Implementation Plan

1. Start with one module (e.g., boards)
2. Create the directory structure
3. Create test files for each application file
4. Verify tests pass
5. Repeat for other modules

### Resolving Common Issues

1. **Test Discovery Problems**
   - Make sure test files follow naming conventions (end with `_test.py`)
   - Check that test functions start with `test_`
   - Ensure no conflicting `__init__.py` files breaking imports

2. **Fixture Access Issues**
   - Use proper pytest fixture importing
   - Verify fixture scope (function, module, session)

3. **Path/Import Issues**
   - Use absolute imports
   - Ensure the Python path includes the workspace root
