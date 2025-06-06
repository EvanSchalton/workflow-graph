#!/usr/bin/env python3

from api.prompts.models.task_prompt import TaskPrompt
from pydantic import ValidationError

def test_validation():
    print("Testing TaskPrompt validation...")
    
    try:
        # This should fail validation
        prompt = TaskPrompt(
            name="",
            prompt_template="test template",
            task_type="test_type",
            variables=[]
        )
        print(f"ERROR: Empty name was accepted: {prompt.name}")
    except ValidationError as e:
        print(f"SUCCESS: Empty name was rejected: {e}")
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
    
    try:
        # This should fail validation
        prompt = TaskPrompt(
            name="name@invalid",
            prompt_template="test template",
            task_type="test_type",
            variables=[]
        )
        print(f"ERROR: Invalid name was accepted: {prompt.name}")
    except ValidationError as e:
        print(f"SUCCESS: Invalid name was rejected: {e}")
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    test_validation()
