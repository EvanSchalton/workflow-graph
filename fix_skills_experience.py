#!/usr/bin/env python3
"""
Script to fix specific type issues in skills_experience_test.py
"""

import re
from pathlib import Path

def fix_skills_experience_test():
    """Fix type issues in the skills_experience_test.py file."""
    file_path = Path('/workspaces/workflow-graph/tests/test_hr/test_services/test_resume/skills_experience_test.py')
    content = file_path.read_text()
    
    # Add assert resume.id is not None for all functions that use resume.id
    patterns = [
        # Pattern for functions that create resume and then use resume.id
        (
            r'(resume = await create_resume\(test_session, sample_resume_data\))\n(\s+)([^=\n]*resume\.id)',
            r'\1\n\2assert resume.id is not None, "Resume should have an ID after creation"\n\2\3'
        ),
        # Pattern for functions that use add_experience_to_resume  
        (
            r'await add_experience_to_resume\(test_session, resume\.id,',
            r'await add_experience_to_resume(test_session, resume.id,'
        ),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Fix the specific function signatures that don't have type hints
    signatures_to_fix = [
        (r'async def (test_add_skill_case_insensitive)\(test_session, sample_resume_data\):', 
         r'async def \1(test_session: AsyncSession, sample_resume_data: Dict[str, Any]) -> None:'),
        (r'async def (test_add_skill_empty_string)\(test_session, sample_resume_data\):', 
         r'async def \1(test_session: AsyncSession, sample_resume_data: Dict[str, Any]) -> None:'),
        (r'async def (test_add_skill_whitespace_only)\(test_session, sample_resume_data\):', 
         r'async def \1(test_session: AsyncSession, sample_resume_data: Dict[str, Any]) -> None:'),
        (r'async def (test_add_skill_resume_not_found)\(test_session\):', 
         r'async def \1(test_session: AsyncSession) -> None:'),
        (r'async def (test_remove_skill_success)\(test_session, sample_resume_data\):', 
         r'async def \1(test_session: AsyncSession, sample_resume_data: Dict[str, Any]) -> None:'),
        (r'async def (test_remove_skill_not_present)\(test_session, sample_resume_data\):', 
         r'async def \1(test_session: AsyncSession, sample_resume_data: Dict[str, Any]) -> None:'),
        (r'async def (test_remove_skill_case_insensitive)\(test_session, sample_resume_data\):', 
         r'async def \1(test_session: AsyncSession, sample_resume_data: Dict[str, Any]) -> None:'),
        (r'async def (test_remove_skill_resume_not_found)\(test_session\):', 
         r'async def \1(test_session: AsyncSession) -> None:'),
        (r'async def (test_add_experience_success)\(test_session, sample_resume_data\):', 
         r'async def \1(test_session: AsyncSession, sample_resume_data: Dict[str, Any]) -> None:'),
        (r'async def (test_add_experience_future_dates)\(test_session, sample_resume_data\):', 
         r'async def \1(test_session: AsyncSession, sample_resume_data: Dict[str, Any]) -> None:'),
        (r'async def (test_add_experience_end_before_start)\(test_session, sample_resume_data, test_uuid: str\):', 
         r'async def \1(test_session: AsyncSession, sample_resume_data: Dict[str, Any], test_uuid: str) -> None:'),
        (r'async def (test_add_experience_resume_not_found)\(test_session\):', 
         r'async def \1(test_session: AsyncSession) -> None:'),
        (r'async def (test_update_resume_experience_success)\(test_session, sample_resume_data\):', 
         r'async def \1(test_session: AsyncSession, sample_resume_data: Dict[str, Any]) -> None:'),
        (r'async def (test_update_resume_experience_empty_list)\(test_session, sample_resume_data\):', 
         r'async def \1(test_session: AsyncSession, sample_resume_data: Dict[str, Any]) -> None:'),
        (r'async def (test_update_resume_experience_not_found)\(test_session\):', 
         r'async def \1(test_session: AsyncSession) -> None:'),
        (r'async def (test_calculate_skill_match_perfect_match)\(test_session, sample_resume_data\):', 
         r'async def \1(test_session: AsyncSession, sample_resume_data: Dict[str, Any]) -> None:'),
        (r'async def (test_calculate_skill_match_partial_match)\(test_session, sample_resume_data\):', 
         r'async def \1(test_session: AsyncSession, sample_resume_data: Dict[str, Any]) -> None:'),
        (r'async def (test_calculate_skill_match_no_match)\(test_session, sample_resume_data\):', 
         r'async def \1(test_session: AsyncSession, sample_resume_data: Dict[str, Any]) -> None:'),
        (r'async def (test_calculate_skill_match_empty_required)\(test_session, sample_resume_data\):', 
         r'async def \1(test_session: AsyncSession, sample_resume_data: Dict[str, Any]) -> None:'),
        (r'async def (test_calculate_skill_match_case_insensitive)\(test_session, sample_resume_data\):', 
         r'async def \1(test_session: AsyncSession, sample_resume_data: Dict[str, Any]) -> None:'),
        (r'async def (test_calculate_skill_match_resume_not_found)\(test_session\):', 
         r'async def \1(test_session: AsyncSession) -> None:'),
    ]
    
    for pattern, replacement in signatures_to_fix:
        content = re.sub(pattern, replacement, content)
    
    file_path.write_text(content)
    print(f"Fixed {file_path}")

def main():
    fix_skills_experience_test()

if __name__ == '__main__':
    main()
