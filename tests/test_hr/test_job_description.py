"""
Tests for the JobDescription model.
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from api.hr.models.job_description import (
    JobDescription,
    JobDescriptionCreate,
    JobDescriptionUpdate, 
    JobDescriptionRead,
    ExperienceLevel
)


@pytest.fixture
def sample_job_description_data(test_uuid: str) -> Dict[str, Any]:
    """Create sample job description data for testing."""
    return {
        "title": f"Senior Software Engineer {test_uuid[:8]}",
        "description": f"We are looking for a skilled software engineer {test_uuid}",
        "required_skills": ["Python", "FastAPI", "SQLAlchemy", "PostgreSQL"],
        "experience_level": ExperienceLevel.SENIOR,
        "department": f"Engineering {test_uuid[:8]}"
    }


def test_job_description_title_validation(test_uuid: str) -> None:
    """Test custom title validation logic."""
    # Empty title should raise error
    with pytest.raises(ValueError, match="Job title cannot be empty"):
        JobDescription.model_validate({
            "title": "",
            "description": f"Test description {test_uuid}",
            "experience_level": "senior"
        })
    
    # Whitespace-only title should raise error
    with pytest.raises(ValueError, match="Job title cannot be empty"):
        JobDescription.model_validate({
            "title": "   ",
            "description": f"Test description {test_uuid}", 
            "experience_level": "senior"
        })
    
    # Valid title should be stripped when using model_validate
    job_desc = JobDescription.model_validate({
        "title": "  Software Engineer  ",
        "description": f"Test description {test_uuid}",
        "experience_level": "senior"
    })
    assert job_desc.title == "Software Engineer"


def test_job_description_experience_level_validation(test_uuid: str) -> None:
    """Test custom experience level validation logic."""
    # String input should be converted to enum
    job_desc = JobDescription.model_validate({
        "title": f"Software Engineer {test_uuid[:8]}",
        "description": f"Test description {test_uuid}",
        "experience_level": "senior"
    })
    assert job_desc.experience_level == ExperienceLevel.SENIOR
    
    # Case insensitive conversion
    job_desc = JobDescription.model_validate({
        "title": f"Junior Engineer {test_uuid[:8]}", 
        "description": f"Test description {test_uuid}",
        "experience_level": "JUNIOR"
    })
    assert job_desc.experience_level == ExperienceLevel.JUNIOR
    
    # Invalid experience level should raise error
    with pytest.raises(ValueError, match="Experience level must be one of"):
        JobDescription.model_validate({
            "title": f"Software Engineer {test_uuid[:8]}",
            "description": f"Test description {test_uuid}", 
            "experience_level": "invalid"
        })


def test_job_description_required_skills_validation(test_uuid: str) -> None:
    """Test custom required_skills validation and cleaning logic."""
    # JSON string input should be parsed
    job_desc = JobDescription.model_validate({
        "title": f"Software Engineer {test_uuid[:8]}",
        "description": f"Test description {test_uuid}",
        "experience_level": "senior",
        "required_skills": '["Python", "JavaScript"]'
    })
    assert job_desc.required_skills == ["Python", "JavaScript"]
    
    # Empty skills should be filtered out
    job_desc = JobDescription.model_validate({
        "title": f"Software Engineer {test_uuid[:8]}",
        "description": f"Test description {test_uuid}", 
        "experience_level": "senior",
        "required_skills": ["Python", "", "JavaScript", "   "]
    })
    assert job_desc.required_skills == ["Python", "JavaScript"]
    
    # Invalid JSON string should raise error
    with pytest.raises(ValueError, match="Required skills must be a list of strings"):
        JobDescription.model_validate({
            "title": f"Software Engineer {test_uuid[:8]}",
            "description": f"Test description {test_uuid}",
            "experience_level": "senior", 
            "required_skills": "invalid json"
        })


def test_job_description_has_skill_method(sample_job_description_data: Dict[str, Any]) -> None:
    """Test the has_skill method business logic."""
    job_desc = JobDescription.model_validate(sample_job_description_data)
    
    assert job_desc.has_skill("Python") is True
    assert job_desc.has_skill("python") is True  # Case insensitive
    assert job_desc.has_skill("Java") is False


def test_job_description_add_skill_method(sample_job_description_data: Dict[str, Any]) -> None:
    """Test the add_skill method business logic."""
    job_desc = JobDescription.model_validate(sample_job_description_data)
    initial_skill_count = len(job_desc.required_skills)
    
    # Add new skill
    job_desc.add_skill("Docker")
    assert len(job_desc.required_skills) == initial_skill_count + 1
    assert job_desc.has_skill("Docker") is True
    
    # Adding duplicate skill shouldn't increase count
    job_desc.add_skill("Docker")
    assert len(job_desc.required_skills) == initial_skill_count + 1


def test_job_description_remove_skill_method(sample_job_description_data: Dict[str, Any]) -> None:
    """Test the remove_skill method business logic."""
    job_desc = JobDescription.model_validate(sample_job_description_data)
    
    # Remove existing skill
    result = job_desc.remove_skill("Python")
    assert result is True
    assert job_desc.has_skill("Python") is False
    
    # Remove non-existing skill
    result = job_desc.remove_skill("Java")
    assert result is False


def test_job_description_matches_skills_method(sample_job_description_data: Dict[str, Any]) -> None:
    """Test the matches_skills method business logic."""
    job_desc = JobDescription.model_validate(sample_job_description_data)
    
    # Perfect match
    candidate_skills = ["Python", "FastAPI", "SQLAlchemy", "PostgreSQL"]
    score = job_desc.matches_skills(candidate_skills)
    assert score == 1.0
    
    # Partial match
    candidate_skills = ["Python", "FastAPI"]
    score = job_desc.matches_skills(candidate_skills)
    assert score == 0.5  # 2 out of 4 skills
    
    # No match
    candidate_skills = ["Java", "Spring"]
    score = job_desc.matches_skills(candidate_skills)
    assert score == 0.0
    
    # Empty candidate skills
    score = job_desc.matches_skills([])
    assert score == 0.0
    
    # Job with no required skills
    job_desc.required_skills = []
    score = job_desc.matches_skills(["Python"])
    assert score == 1.0


@pytest.mark.parametrize("experience_level,expected", [
    ("junior", ExperienceLevel.JUNIOR),
    ("mid", ExperienceLevel.MID),
    ("senior", ExperienceLevel.SENIOR),
    ("lead", ExperienceLevel.LEAD),
    ("expert", ExperienceLevel.EXPERT),
])
def test_job_description_experience_level_enum_conversion(experience_level: str, expected: ExperienceLevel, test_uuid: str) -> None:
    """Test experience level string to enum conversion."""
    job_desc = JobDescription(
        title=f"Software Engineer {test_uuid[:8]}",
        description=f"Test description {test_uuid}",
        experience_level=experience_level
    )
    assert job_desc.experience_level == expected


def test_job_description_create_schema(sample_job_description_data: Dict[str, Any]) -> None:
    """Test the JobDescriptionCreate schema validation."""
    # Remove id and timestamps for create schema
    create_data = {k: v for k, v in sample_job_description_data.items() 
                   if k not in ['id', 'created_at', 'updated_at']}
    
    job_desc_create = JobDescriptionCreate.model_validate(create_data)
    assert job_desc_create.title == sample_job_description_data["title"]
    assert job_desc_create.description == sample_job_description_data["description"]
    assert job_desc_create.experience_level == sample_job_description_data["experience_level"]


def test_job_description_update_schema() -> None:
    """Test the JobDescriptionUpdate schema validation."""
    update_data = {
        "title": "Updated Title",
        "required_skills": ["Updated Skill"]
    }
    
    job_desc_update = JobDescriptionUpdate.model_validate(update_data)
    assert job_desc_update.title == "Updated Title"
    assert job_desc_update.description is None  # Should be optional
    assert job_desc_update.required_skills == ["Updated Skill"]


def test_job_description_read_schema(sample_job_description_data: Dict[str, Any]) -> None:
    """Test the JobDescriptionRead schema validation."""
    # Add required fields for read schema
    read_data = {
        **sample_job_description_data,
        "id": 1,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    job_desc_read = JobDescriptionRead.model_validate(read_data)
    assert job_desc_read.id == 1
    assert job_desc_read.title == sample_job_description_data["title"]
    assert isinstance(job_desc_read.created_at, datetime)
    assert isinstance(job_desc_read.updated_at, datetime)


def test_job_description_string_representation(sample_job_description_data: Dict[str, Any]) -> None:
    """Test string representation methods."""
    job_desc = JobDescription.model_validate({**sample_job_description_data, "id": 42})
    
    str_repr = str(job_desc)
    assert "JobDescription(id=42" in str_repr
    assert sample_job_description_data["title"] in str_repr
    assert "senior" in str_repr
    
    repr_repr = repr(job_desc)
    assert "JobDescription(id=42" in repr_repr
    assert sample_job_description_data["title"] in repr_repr
    assert "skills=4" in repr_repr  # Should show count of skills
