#!/usr/bin/env python3

from api.prompts.models.task_prompt import TaskPrompt
from pydantic import ValidationError

def test_validation():
    print("Testing TaskPrompt validation...")
    
    # Check model fields
    print("Model fields:")
    for name, field in TaskPrompt.model_fields.items():
        print(f"  {name}: {field}")
    
    # Check if validators are registered
    print("\nModel validators:")
    print(f"  __pydantic_validator__: {hasattr(TaskPrompt, '__pydantic_validator__')}")
    print(f"  __pydantic_core_schema__: {hasattr(TaskPrompt, '__pydantic_core_schema__')}")
    
    # Try model creation with dict
    print("\nTrying model_validate with dict:")
    try:
        prompt = TaskPrompt.model_validate({
            "name": "",
            "prompt_template": "test template",
            "task_type": "test_type"
        })
        print(f"ERROR: Empty name was accepted: '{prompt.name}'")
    except ValidationError as e:
        print(f"SUCCESS: Empty name was rejected: {e}")
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    test_validation()
