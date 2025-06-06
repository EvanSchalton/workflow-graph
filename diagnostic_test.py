"""
Diagnostic test to understand Pydantic validation behavior.
"""

from pydantic import ValidationError

from api.prompts.models.task_prompt import TaskPrompt


def test_diagnostic_validation() -> None:
    """Test to understand current validation behavior."""
    # Test that should fail validation
    try:
        prompt = TaskPrompt(
            name="",  # Empty name should fail
            prompt_template="test",
            task_type="test"
        )
        print(f"Created prompt with empty name: {prompt.name}")
        print("ERROR: Validation did not fail as expected!")
    except ValidationError as e:
        print(f"Validation failed as expected: {e}")
    
    # Test normalization
    try:
        prompt = TaskPrompt(
            name="  test  ",
            prompt_template="test",
            task_type="Code Review"
        )
        print(f"Name after creation: '{prompt.name}'")
        print(f"Task type after creation: '{prompt.task_type}'")
    except Exception as e:
        print(f"Error during creation: {e}")


if __name__ == "__main__":
    test_diagnostic_validation()
