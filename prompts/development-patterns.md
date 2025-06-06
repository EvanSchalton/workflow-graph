# Development Patterns for Agentic Workforce API

**Note**: This document should be updated as new guidance and patterns are established during development.

## Key Patterns Established

### General Coding Standards
- **Type hint everything**: All functions, methods, variables, and parameters should have proper type hints throughout the codebase
- **Use proper Pydantic methods**: Use `Model.model_validate(data)` for creating instances from dictionaries, but use direct constructor `Model(field=value)` when passing individual parameters
- **Handle type checking pragmatically**: Install type stubs for packages when available, but use `# type: ignore` comments when necessary rather than manually creating stubs

### Dependency Management
- **Use Poetry for dependency management**: All package installations and dependency management should use Poetry, not pip
- **Add dependencies with Poetry**: Use `poetry add <package>` for runtime dependencies and `poetry add --group dev <package>` for development dependencies
- **Install dependencies**: Use `poetry install` to install all dependencies from the lock file
- **Update dependencies**: Use `poetry update` to update dependencies while respecting version constraints
- **Virtual environment**: Poetry automatically manages the virtual environment; use `poetry shell` or `poetry run <command>` to execute commands in the environment

### Test Directory Structure
- **NO `__init__.py` files in tests directory**: Pytest discovery works better without them and avoids import conflicts
- Follow structure: `tests/test_module/test_submodule/test_file.py`

### Testing Approach
- **NO standalone test scripts**: All tests must be in the `tests/` directory structure
- **Use `invoke` command for task execution**: Instead of direct terminal commands, use invoke tasks
- **Run tests via pytest**: Always use `pytest` command from the proper test directory
- **Use test functions not classes**: Prefer `def test_*()` functions over `class Test*:` classes
- **Type hint everything**: All test functions, fixtures, and variables should have proper type hints
- **Use test_uuid fixture**: Use `test_uuid` fixture from conftest for traceability, not hardcoded UUIDs
- **Create factory fixtures**: Use helper test-case factory fixtures that include `test_uuid` in data for traceability
- **Traceable test data**: Include `test_uuid` in descriptions and other fields so test data can be traced in logs/DB
- **Use pytest parameterization**: Use `@pytest.mark.parametrize` for testing multiple scenarios efficiently
- **Don't test built-ins**: Don't write tests for built-in functionality like enum values or Python core features
- **NO manual testing in terminal**: If you need to test behavior, write a proper test function instead of running manual commands
- **Write tests to verify actual behavior**: If tests are failing and you're unsure why, add diagnostic tests to understand the current behavior
- **Don't test Pydantic basics**: Don't test that constructor parameters are assigned to model fields - test custom validators, business logic, and edge cases
- **Use proper Pydantic methods**: Use `Model.model_validate(data)` for creating instances from dictionaries, but use direct constructor `Model(field=value)` when passing individual parameters
- **Fix all warnings**: Address deprecation warnings, type warnings, and other warnings identified during testing

### TDD Implementation
- Write failing tests first (Red)
- Implement minimal code to pass (Green) 
- Refactor while keeping tests green
- Complete one sub-task at a time with user permission

### Task Management
- Mark completed tasks with `[x]` in task list files
- Update "Relevant Files" section as files are created/modified
- **Run quality checks before completion**: Run `mypy` and `ruff` to check for type errors and code quality issues
- **Fix all quality issues**: Address any errors, warnings, or style issues identified by static analysis tools
- **Verify complete test coverage**: Only mark a task as complete when both `invoke test` and `invoke check` run clean without filtering (no errors across the entire codebase)
- Stop after each sub-task completion and wait for user approval

### SQLModel/SQLAlchemy Patterns
- Use `Column` with `sa_column` parameter for complex types like arrays
- Import SQLAlchemy types when SQLModel doesn't support them natively
- Use PostgreSQL ARRAY type for list fields: `sa_column=Column(ARRAY(String))`

