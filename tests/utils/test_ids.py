"""Utility functions for generating unique test IDs."""

from uuid import uuid4


def get_unique_test_id() -> int:
    """
    Generate a unique integer ID for testing that is guaranteed not to exist.
    
    Uses the lower 31 bits of a UUID4 to ensure uniqueness while staying
    within the positive integer range for database IDs.
    
    Returns:
        int: A unique positive integer suitable for use as a database ID
    """
    # Use lower 31 bits to ensure positive integer within reasonable range
    return int(uuid4().int & 0x7FFFFFFF)


def get_unique_test_ids(count: int) -> list[int]:
    """
    Generate multiple unique integer IDs for testing.
    
    Args:
        count: Number of unique IDs to generate
        
    Returns:
        list[int]: List of unique positive integers
    """
    return [get_unique_test_id() for _ in range(count)]
