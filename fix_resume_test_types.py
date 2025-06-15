#!/usr/bin/env python3
"""
Script to automatically add return type annotations to test functions in resume_test.py
"""

import re

def fix_resume_test_types():
    file_path = '/workspaces/workflow-graph/tests/test_hr/resume_test.py'
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to match test functions without return type annotations
    pattern = r'^(def test_[^(]+\([^)]*\)):(\s*\n)'
    
    def replace_func(match):
        func_def = match.group(1)
        whitespace = match.group(2)
        
        # Add -> None to the function definition
        if ' -> ' not in func_def:
            func_def += ' -> None'
        
        return func_def + ':' + whitespace
    
    # Apply the replacement
    new_content = re.sub(pattern, replace_func, content, flags=re.MULTILINE)
    
    # Also fix any other untyped functions (non-test functions)
    pattern2 = r'^(def [^(]+\([^)]*\)):(\s*\n)'
    
    def replace_func2(match):
        func_def = match.group(1)
        whitespace = match.group(2)
        
        # Skip if it already has a return type annotation
        if ' -> ' in func_def:
            return match.group(0)
        
        # Skip fixture functions which might have different return types
        if '@pytest.fixture' in content[max(0, match.start() - 100):match.start()]:
            return match.group(0)
        
        # Add -> None to the function definition
        func_def += ' -> None'
        
        return func_def + ':' + whitespace
    
    # Apply the second replacement
    new_content = re.sub(pattern2, replace_func2, new_content, flags=re.MULTILINE)
    
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print("Fixed return type annotations in resume_test.py")

if __name__ == '__main__':
    fix_resume_test_types()
