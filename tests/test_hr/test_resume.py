"""
Tests for the Resume model.
"""

import pytest
from datetime import datetime
from typing import List, Dict, Any

from api.hr.models.resume import (
    Resume, 
    ResumeCreate, 
    ResumeUpdate, 
    ResumeRead,
    ExperienceEntry,
    EducationEntry
)


@pytest.fixture
def sample_experience_entry(test_uuid: str) -> Dict[str, Any]:
    """Create a sample experience entry for testing."""
    return {
        "company": f"Test Company {test_uuid[:8]}",
        "position": f"Software Engineer {test_uuid[:8]}",
        "start_date": "2020-01-01",
        "end_date": "2022-12-31",
        "description": f"Worked on test projects {test_uuid}"
    }


@pytest.fixture
def sample_education_entry(test_uuid: str) -> Dict[str, Any]:
    """Create a sample education entry for testing."""
    return {
        "institution": f"Test University {test_uuid[:8]}",
        "degree": f"Computer Science {test_uuid[:8]}",
        "field_of_study": "Software Engineering",
        "graduation_year": 2020,
        "gpa": 3.8
    }


@pytest.fixture
def sample_resume_data(test_uuid: str, sample_experience_entry: Dict[str, Any], sample_education_entry: Dict[str, Any]) -> Dict[str, Any]:
    """Create sample resume data for testing."""
    return {
        "name": f"John Doe {test_uuid[:8]}",
        "email": f"john.doe.{test_uuid[:8]}@example.com",
        "phone": "+1-555-123-4567",
        "summary": f"Experienced software engineer {test_uuid}",
        "skills": ["Python", "FastAPI", "SQLAlchemy"],
        "experience": [sample_experience_entry],
        "education": [sample_education_entry],
        "performance_history": {
            "projects_completed": 10,
            "average_rating": 4.5,
            "total_tasks": 100
        }
    }


def test_resume_name_validation(test_uuid: str) -> None:
    """Test custom name validation logic."""
    # Empty name should raise error (Pydantic min_length constraint)
    with pytest.raises(ValueError, match="String should have at least 1 character"):
        Resume.model_validate({
            "name": "", 
            "email": f"test-{test_uuid}@example.com"
        })
    
    # Whitespace-only name should raise error (custom validator)
    with pytest.raises(ValueError, match="Name cannot be empty"):
        Resume.model_validate({
            "name": "   ", 
            "email": f"test-{test_uuid}@example.com"
        })
    
    # Valid name should be stripped
    resume = Resume.model_validate({
        "name": "  John Doe  ", 
        "email": f"test-{test_uuid}@example.com"
    })
    assert resume.name == "John Doe"


def test_resume_email_validation(test_uuid: str) -> None:
    """Test custom email validation logic."""
    # Invalid email should raise error
    with pytest.raises(ValueError, match="Invalid email format"):
        Resume.model_validate({
            "name": f"John Doe {test_uuid[:8]}", 
            "email": "invalid-email"
        })
    
    # Valid email should be normalized
    resume = Resume.model_validate({
        "name": f"John Doe {test_uuid[:8]}", 
        "email": f"  TEST-{test_uuid}@EXAMPLE.COM  "
    })
    assert resume.email == f"test-{test_uuid}@example.com"


def test_resume_skills_validation(test_uuid: str) -> None:
    """Test custom skills validation and cleaning logic."""
    # Empty skills should be filtered out
    resume = Resume.model_validate({
        "name": f"John Doe {test_uuid[:8]}", 
        "email": f"test-{test_uuid}@example.com", 
        "skills": ["Python", "", "JavaScript", "   "]
    })
    assert resume.skills == ["Python", "JavaScript"]


def test_resume_has_skill_method(sample_resume_data: Dict[str, Any]) -> None:
    """Test the has_skill method business logic."""
    resume = Resume.model_validate(sample_resume_data)
    
    assert resume.has_skill("Python") is True
    assert resume.has_skill("python") is True  # Case insensitive
    assert resume.has_skill("Java") is False


def test_resume_add_skill_method(sample_resume_data: Dict[str, Any]) -> None:
    """Test the add_skill method business logic."""
    resume = Resume.model_validate(sample_resume_data)
    initial_skill_count = len(resume.skills)
    
    # Add new skill
    resume.add_skill("Java")
    assert len(resume.skills) == initial_skill_count + 1
    assert resume.has_skill("Java") is True
    
    # Adding duplicate skill shouldn't increase count
    resume.add_skill("Java")
    assert len(resume.skills) == initial_skill_count + 1


def test_resume_remove_skill_method(sample_resume_data: Dict[str, Any]) -> None:
    """Test the remove_skill method business logic."""
    resume = Resume.model_validate(sample_resume_data)
    
    # Remove existing skill
    result = resume.remove_skill("Python")
    assert result is True
    assert resume.has_skill("Python") is False
    
    # Remove non-existing skill
    result = resume.remove_skill("Java")
    assert result is False


def test_resume_calculate_experience_years(sample_resume_data: Dict[str, Any]) -> None:
    """Test the calculate_experience_years method business logic."""
    resume = Resume.model_validate(sample_resume_data)
    years = resume.calculate_experience_years()
    
    # Should calculate based on experience entries
    assert years > 0
    assert isinstance(years, float)


def test_resume_skill_match_score(sample_resume_data: Dict[str, Any]) -> None:
    """Test the skill_match_score method business logic."""
    resume = Resume.model_validate(sample_resume_data)
    
    # Perfect match
    required_skills = ["Python", "FastAPI"]
    score = resume.skill_match_score(required_skills)
    assert score == 1.0
    
    # Partial match
    required_skills = ["Python", "FastAPI", "Java", "C++"]
    score = resume.skill_match_score(required_skills)
    assert 0.0 < score < 1.0
    
    # No match
    required_skills = ["Java", "C++"]
    score = resume.skill_match_score(required_skills)
    assert score == 0.0
    
    # Empty required skills
    score = resume.skill_match_score([])
    assert score == 1.0


def test_resume_create_schema(sample_resume_data: Dict[str, Any]) -> None:
    """Test the ResumeCreate schema validation."""
    # Remove id and timestamps for create schema
    create_data = {k: v for k, v in sample_resume_data.items() 
                   if k not in ['id', 'created_at', 'updated_at']}
    
    resume_create = ResumeCreate.model_validate(create_data)
    assert resume_create.name == sample_resume_data["name"]
    assert resume_create.email == sample_resume_data["email"]


def test_resume_update_schema(test_uuid: str) -> None:
    """Test the ResumeUpdate schema validation."""
    update_data = {
        "name": f"Updated Name {test_uuid[:8]}",
        "skills": ["Updated Skill"]
    }
    
    resume_update = ResumeUpdate.model_validate(update_data)
    assert resume_update.name == f"Updated Name {test_uuid[:8]}"
    assert resume_update.email is None  # Should be optional
    assert resume_update.skills == ["Updated Skill"]


def test_resume_read_schema(sample_resume_data: Dict[str, Any]) -> None:
    """Test the ResumeRead schema validation."""
    # Add required fields for read schema
    read_data = {
        **sample_resume_data,
        "id": 1,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    resume_read = ResumeRead.model_validate(read_data)
    assert resume_read.id == 1
    assert resume_read.name == sample_resume_data["name"]
    assert isinstance(resume_read.created_at, datetime)
    assert isinstance(resume_read.updated_at, datetime)


def test_experience_entry_model(test_uuid: str) -> None:
    """Test the ExperienceEntry model."""
    entry_data = {
        "company": f"Test Company {test_uuid[:8]}",
        "position": f"Software Engineer {test_uuid[:8]}",
        "start_date": "2020-01-01",
        "end_date": "2022-12-31",
        "description": f"Worked on test projects {test_uuid}"
    }
    
    entry = ExperienceEntry.model_validate(entry_data)
    assert entry.company == f"Test Company {test_uuid[:8]}"
    assert entry.position == f"Software Engineer {test_uuid[:8]}"
    assert entry.start_date == "2020-01-01"
    assert entry.end_date == "2022-12-31"
    assert entry.description == f"Worked on test projects {test_uuid}"


def test_education_entry_model(test_uuid: str) -> None:
    """Test the EducationEntry model."""
    entry_data = {
        "institution": f"Test University {test_uuid[:8]}",
        "degree": f"Bachelor of Science {test_uuid[:8]}",
        "field_of_study": "Computer Science",
        "graduation_year": 2020,
        "gpa": 3.8
    }
    
    entry = EducationEntry.model_validate(entry_data)
    assert entry.institution == f"Test University {test_uuid[:8]}"
    assert entry.degree == f"Bachelor of Science {test_uuid[:8]}"
    assert entry.field_of_study == "Computer Science"
    assert entry.graduation_year == 2020
    assert entry.gpa == 3.8


def test_resume_string_representation(sample_resume_data: Dict[str, Any]) -> None:
    """Test string representation methods."""
    resume = Resume.model_validate({**sample_resume_data, "id": 42})
    
    str_repr = str(resume)
    assert "Resume(id=42" in str_repr
    assert sample_resume_data["name"] in str_repr
    assert sample_resume_data["email"] in str_repr
    
    repr_repr = repr(resume)
    assert "Resume(id=42" in repr_repr
    assert sample_resume_data["name"] in repr_repr
    assert "skills=3" in repr_repr  # Should show count of skills


