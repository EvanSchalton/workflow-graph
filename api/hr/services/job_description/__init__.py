"""
JobDescription service for CRUD operations.
This service acts as an orchestration layer that imports and delegates to individual business logic functions.
According to the one-function-per-file pattern, each business logic function is in its own file.
"""

# Import all business logic functions from individual files
from .get_job_description import get_job_description
from .get_job_descriptions import get_job_descriptions
from .create_job_description import create_job_description
from .update_job_description import update_job_description
from .delete_job_description import delete_job_description
from .add_skill_to_job_description import add_skill_to_job_description
from .remove_skill_from_job_description import remove_skill_from_job_description
from .find_matching_job_descriptions import find_matching_job_descriptions

# Re-export all functions to maintain compatibility
__all__ = [
    "get_job_description",
    "get_job_descriptions", 
    "create_job_description",
    "update_job_description",
    "delete_job_description",
    "add_skill_to_job_description",
    "remove_skill_from_job_description",
    "find_matching_job_descriptions"
]
