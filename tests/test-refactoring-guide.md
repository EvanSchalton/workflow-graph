# Test Refactoring Guide

This document provides guidance on how to continue refactoring the test directory structure to mirror the application code structure.

## Progress So Far

We've started refactoring the test files for the following components:

1. **Jira Board Routes**:
   - Created `/tests/test_jira/routes/boards/get_boards_test.py`
   - Created `/tests/test_jira/routes/boards/get_board_by_id_test.py`
   - Created `/tests/test_jira/routes/boards/create_board_test.py`
   - Created `/tests/test_jira/routes/boards/update_board_test.py`
   - Created `/tests/test_jira/routes/boards/delete_board_with_events_test.py`

2. **Jira Ticket Routes**:
   - Created `/tests/test_jira/routes/tickets/get_tickets_test.py`
   - Created `/tests/test_jira/routes/tickets/get_ticket_by_id_test.py`
   - Created `/tests/test_jira/routes/tickets/create_ticket_test.py`

3. **Jira Column Routes**:
   - Created `/tests/test_jira/routes/columns/create_column_test.py`

4. **Other Jira Components**:
   - Created `/tests/test_jira/webhook_manager_test.py`

## How to Continue Refactoring

Follow these steps to continue refactoring the tests:

1. **Identify Application Code Files**:
   - Use `file_search` to list all application code files you need to test
   - Example: `file_search api/jira/**/*.py`

2. **Check for Existing Tests**:
   - Use `file_search` to find any existing test files
   - Example: `file_search tests/test_jira/*_test.py`

3. **Create Mirrored Test Directory Structure**:
   - Create test directories that mirror the application code structure
   - Example: If there's `api/jira/routes/webhooks/create_webhook.py`, create `tests/test_jira/routes/webhooks/create_webhook_test.py`

4. **Move Test Code**:
   - Extract relevant test functions from existing test files
   - Create new test files with the same structure as the application code
   - Make sure each test file focuses on testing a single application code file

5. **Update Imports**:
   - Update imports in the new test files if needed

6. **Run Tests**:
   - After refactoring, run the tests to ensure they still pass

## Guidelines

1. **One Test File Per Application File**:
   - Each application code file should have a corresponding test file
   - Example: `api/jira/models/board.py` -> `tests/test_jira/models/board_test.py`

2. **Naming Convention**:
   - Test directories should start with `test_`
   - Test files should end with `_test.py`

3. **Test Functions**:
   - Each test function should test a specific aspect of the application code
   - Include multiple test cases for different scenarios (success, failure, edge cases)

4. **Use Test Fixtures**:
   - Reuse existing test fixtures for setup and teardown

## Next Steps

Focus on the following areas next:

1. Complete refactoring of the remaining Jira tests
2. Move to HR, Orchestration, and other modules
3. Update any references to the old test files

Remember to follow the 1-function-per-file rule for the application code and the corresponding 1-test-file-per-function-file rule for tests.
