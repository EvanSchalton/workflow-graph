#!/usr/bin/env python3
"""
Script to systematically fix type hints in all test files.
"""

import re
from pathlib import Path

def fix_all_test_files():
    """Fix type hints in all test files."""
    test_files = [
        # Skills experience test file
        ('/workspaces/workflow-graph/tests/test_hr/test_services/test_resume/skills_experience_test.py', [
            (r'sample_resume_data: Dict\[str, Any\]', r'sample_resume_data: ResumeCreate'),
        ]),
        
        # Resume CRUD test file
        ('/workspaces/workflow-graph/tests/test_hr/test_services/test_resume/resume_crud_test.py', [
            (r'async def test_([^(]+)\(test_session, sample_resume_data\):', r'async def test_\1(test_session: AsyncSession, sample_resume_data: ResumeCreate) -> None:'),
            (r'async def test_([^(]+)\(test_session, sample_resume_data, test_uuid: str\):', r'async def test_\1(test_session: AsyncSession, sample_resume_data: ResumeCreate, test_uuid: str) -> None:'),
            (r'async def test_([^(]+)\(test_session\):', r'async def test_\1(test_session: AsyncSession) -> None:'),
        ]),
        
        # Task assignment test file
        ('/workspaces/workflow-graph/tests/test_orchestration/task_assignment_test.py', [
            (r'def test_([^(]+)\(assignment_factory, test_uuid: str\):', r'def test_\1(assignment_factory, test_uuid: str) -> None:'),
            (r'def test_([^(]+)\(test_uuid: str\):', r'def test_\1(test_uuid: str) -> None:'),
        ]),
        
        # Task test file
        ('/workspaces/workflow-graph/tests/test_orchestration/task_test.py', [
            (r'def test_([^(]+)\(task_factory, test_uuid: str\):', r'def test_\1(task_factory, test_uuid: str) -> None:'),
            (r'def test_([^(]+)\(test_uuid: str\):', r'def test_\1(test_uuid: str) -> None:'),
        ]),
    ]
    
    for file_path, replacements in test_files:
        path = Path(file_path)
        if not path.exists():
            continue
            
        content = path.read_text()
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        path.write_text(content)
        print(f"Fixed {file_path}")

def main():
    fix_all_test_files()

if __name__ == '__main__':
    main()
