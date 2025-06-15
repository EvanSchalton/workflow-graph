#!/usr/bin/env python3
"""
Script to add type hints to test files.
"""

import re
from pathlib import Path

def fix_test_function_signatures(file_path: Path) -> None:
    """Fix test function signatures to add type hints."""
    content = file_path.read_text()
    
    # Common type hint patterns for test functions
    replacements = [
        # Basic test function patterns
        (r'def test_([^(]+)\(client, test_uuid\):', r'def test_\1(client: TestClient, test_uuid: str) -> None:'),
        (r'def test_([^(]+)\(client\):', r'def test_\1(client: TestClient) -> None:'),
        
        # Async test function patterns  
        (r'async def test_([^(]+)\(test_session, sample_resume_data\):', r'async def test_\1(test_session: AsyncSession, sample_resume_data: Dict[str, Any]) -> None:'),
        (r'async def test_([^(]+)\(test_session\):', r'async def test_\1(test_session: AsyncSession) -> None:'),
        (r'async def test_([^(]+)\(test_session, sample_resume_data, test_uuid: str\):', r'async def test_\1(test_session: AsyncSession, sample_resume_data: Dict[str, Any], test_uuid: str) -> None:'),
        
        # Fixture patterns
        (r'def test_([^(]+)\(task_prompt_data: dict\):', r'def test_\1(task_prompt_data: Dict[str, Any]) -> None:'),
        (r'def test_([^(]+)\(task_prompt_data: dict, ([^)]+)\):', r'def test_\1(task_prompt_data: Dict[str, Any], \2) -> None:'),
        
        # More specific patterns that may exist
        (r'def test_([^(]+)\(([^)]*)\):(?!\s*\-\>)', r'def test_\1(\2) -> None:'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Add necessary imports if not present
    if 'from typing import' not in content and ('Dict[str, Any]' in content or 'AsyncSession' in content):
        import_lines = []
        if 'Dict[str, Any]' in content:
            import_lines.append('from typing import Dict, Any')
        if 'AsyncSession' in content:
            import_lines.append('from sqlmodel.ext.asyncio.session import AsyncSession')
        if 'TestClient' in content and 'from fastapi.testclient import TestClient' not in content:
            import_lines.append('from fastapi.testclient import TestClient')
            
        # Find where to insert imports
        lines = content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('"""') and i == 0:
                # Find end of docstring
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().endswith('"""'):
                        insert_pos = j + 2
                        break
                break
            elif line.startswith('import ') or line.startswith('from '):
                # Find end of import block
                for j in range(i, len(lines)):
                    if not (lines[j].startswith('import ') or lines[j].startswith('from ') or lines[j].strip() == ''):
                        insert_pos = j
                        break
                break
        
        if insert_pos > 0:
            for import_line in reversed(import_lines):
                lines.insert(insert_pos, import_line)
            content = '\n'.join(lines)
    
    file_path.write_text(content)

def main():
    """Main function to process all test files."""
    test_dir = Path('/workspaces/workflow-graph/tests')
    
    # Get all Python test files
    test_files = list(test_dir.rglob('*.py'))
    test_files = [f for f in test_files if not f.name.startswith('conftest') and 'test' in f.name]
    
    for file_path in test_files:
        print(f"Processing {file_path}")
        try:
            fix_test_function_signatures(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

if __name__ == '__main__':
    main()
