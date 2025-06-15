# Product Requirements Document: Test Directory Structure Refactoring

## Introduction/Overview

The current test directory structure in the workflow-graph project needs to be refactored to align with the development patterns established in `development-patterns.md`. Currently, tests are organized in a mix of patterns - some follow the application structure while others are grouped by feature or functionality. This refactoring will standardize the test organization to directly mirror the application code directory structure, with each application code file having a corresponding test file.

The goal is to create a clean, predictable test structure where developers can easily locate tests for any given application code file, following the principle of "one application file → one test file" while maintaining 100% test coverage.

## Goals

1. **Mirror Application Structure**: Test directory structure should exactly mirror the `api/` directory structure
2. **Predictable Test Location**: Any application file should have a corresponding test file in the same relative path
3. **Maintain Test Coverage**: Ensure no test coverage is lost during the refactoring process
4. **Standardize Naming**: All test files follow the `[source_filename]_test.py` naming convention
5. **Clean Migration**: Remove old test files that don't fit the new pattern after migrating their content
6. **Preserve Test Utilities**: Maintain shared test fixtures and utilities in appropriate locations

## User Stories

- **As a developer**, I want to easily find tests for any application code file by following a predictable directory structure, so that I can quickly understand and modify tests.
- **As a developer**, I want all tests for a specific function or class to be in one dedicated test file, so that I don't have to search multiple files for related tests.
- **As a maintainer**, I want the test structure to mirror the application structure, so that when I refactor application code, I know exactly where the corresponding tests are located.
- **As a new team member**, I want a consistent test organization pattern, so that I can quickly understand the codebase and contribute effectively.

## Functional Requirements

### 1. Directory Structure Mirroring
- **REQ-1.1**: Create test directories that exactly mirror the `api/` directory structure
- **REQ-1.2**: For each application file `api/path/to/file.py`, create corresponding test file `tests/test_api/test_path/test_to/file_test.py`
- **REQ-1.3**: Maintain the directory hierarchy depth and naming consistency

### 2. Test File Organization  
- **REQ-2.1**: Each application code file gets one corresponding test file
- **REQ-2.2**: All tests for a given function/class must be consolidated into its corresponding test file
- **REQ-2.3**: Test files must follow the naming pattern `[source_filename]_test.py`
- **REQ-2.4**: Test directories must start with `test_` prefix (e.g., `test_api/`, `test_hr/`)

### 3. Migration Process
- **REQ-3.1**: Create target directory structure and test files if they don't exist
- **REQ-3.2**: Identify existing test files that don't match the new pattern
- **REQ-3.3**: Move test functions from old test files to appropriate target test files
- **REQ-3.4**: Remove empty or obsolete test files after migration
- **REQ-3.5**: Preserve all existing test functions and their functionality

### 4. Test Utilities Management
- **REQ-4.1**: Maintain `conftest.py` files at appropriate levels in the hierarchy
- **REQ-4.2**: Organize shared test utilities in `tests/utils/` directory
- **REQ-4.3**: Ensure test fixtures remain accessible to all test files that need them

### 5. Quality Assurance
- **REQ-5.1**: Maintain 100% branch and statement coverage after refactoring
- **REQ-5.2**: All tests must pass after refactoring
- **REQ-5.3**: No `__init__.py` files in test directories (per development patterns)
- **REQ-5.4**: All test files must be discoverable by pytest

## Non-Goals (Out of Scope)

- **Rewriting test logic**: Tests should be moved as-is without changing their functionality
- **Adding new tests**: This is purely a structural refactoring, not test enhancement
- **Performance optimization**: Focus is on organization, not test execution speed
- **Test framework changes**: Continue using existing pytest setup
- **Application code changes**: No modifications to the application code itself

## Technical Considerations

### Current State Analysis
Based on the workspace exploration:
- Application code is organized in `api/` with subdirectories: `cost_tracking/`, `hr/`, `jira/`, `orchestration/`, `prompts/`, `shared/`
- Current tests are in `tests/` with mixed organizational patterns
- Some tests already follow the mirroring pattern (e.g., `tests/test_hr/`, `tests/test_jira/`)
- Some tests are deeply nested (e.g., `tests/test_hr/test_services/test_resume/`)
- Total of 27 test files currently ending with `_test.py`

### Target Structure Example
```
api/hr/models/resume.py → tests/test_api/test_hr/test_models/resume_test.py
api/hr/services/resume/create_resume.py → tests/test_api/test_hr/test_services/test_resume/create_resume_test.py
api/jira/routes/boards/get_board_by_id.py → tests/test_api/test_jira/test_routes/test_boards/get_board_by_id_test.py
```

### Migration Strategy
1. **Phase 1**: Create target directory structure
2. **Phase 2**: Create target test files for each application file
3. **Phase 3**: Migrate test functions from existing files to target files
4. **Phase 4**: Clean up old test files
5. **Phase 5**: Verify coverage and test execution

### Dependencies
- Existing pytest configuration in `pyproject.toml`
- Current `conftest.py` files and fixtures
- Coverage reporting setup
- Import statements in test files may need updates

## Success Metrics

1. **Structural Compliance**: 100% of application code files have corresponding test files in mirrored structure
2. **Test Coverage**: Maintain exact same coverage percentage before and after refactoring
3. **Test Execution**: All tests pass with `pytest` command
4. **Code Quality**: `invoke check` runs clean without errors
5. **Discoverability**: All test files are discoverable by pytest's default discovery rules

## Implementation Phases

### Phase 1: Structure Creation
- Analyze all application code files in `api/`
- Create corresponding test directory structure under `tests/test_api/`
- Create empty test files with proper naming convention

### Phase 2: Content Migration
- Identify existing test files that don't match the target pattern
- Map test functions to their appropriate target test files
- Move test functions while preserving imports and fixtures

### Phase 3: Cleanup and Validation  
- Remove empty or obsolete test files
- Update import statements as needed
- Run full test suite and coverage analysis
- Verify all quality checks pass

## Open Questions

1. **Import Statement Updates**: Should relative imports be updated to absolute imports during migration?
2. **Fixture Scope**: How should module-level fixtures be handled when tests are moved between files?
3. **Test Grouping**: When multiple functions from the same source file have tests scattered across different files, how should they be consolidated?
4. **Legacy Test Files**: Should we preserve any existing test files that serve as integration tests spanning multiple modules?

## Acceptance Criteria

- [ ] Test directory structure exactly mirrors `api/` directory structure
- [ ] Every `.py` file in `api/` has a corresponding `*_test.py` file in `tests/test_api/`
- [ ] All existing test functions are preserved and functional
- [ ] No test coverage is lost (verified with coverage reports)
- [ ] All tests pass with `pytest`
- [ ] `invoke check` runs clean
- [ ] No orphaned or empty test files remain
- [ ] Test discovery works correctly with new structure
