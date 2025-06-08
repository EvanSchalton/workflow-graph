"""
Unit tests for create_resume service function.
"""

import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from api.hr.models.resume import ResumeCreate
from api.hr.services.resume.create_resume import create_resume


class TestCreateResume:
    """Test cases for create_resume function."""

    def test_resume_create_model_validation(self, test_uuid: str) -> None:
        """Test ResumeCreate model validation."""
        # Test valid data
        resume_data = ResumeCreate(
            name=f"Test User {test_uuid}",
            email=f"test.{test_uuid}@example.com",
            skills=["Python", "SQL"]
        )
        assert resume_data.name == f"Test User {test_uuid}"
        assert resume_data.email == f"test.{test_uuid}@example.com"
        assert resume_data.skills == ["Python", "SQL"]

    def test_resume_create_minimal_data(self, test_uuid: str) -> None:
        """Test creating ResumeCreate with minimal data."""
        resume_data = ResumeCreate(
            name=f"Minimal User {test_uuid}",
            email=f"minimal.{test_uuid}@example.com"
        )
        assert resume_data.name == f"Minimal User {test_uuid}"
        assert resume_data.email == f"minimal.{test_uuid}@example.com"
        assert resume_data.skills == []
        assert resume_data.experience == []
        assert resume_data.education == []
        assert resume_data.performance_history == {}

    def test_resume_create_with_complex_data(self, test_uuid: str) -> None:
        """Test creating ResumeCreate with complex data."""
        resume_data = ResumeCreate(
            name=f"Complex User {test_uuid}",
            email=f"complex.{test_uuid}@example.com",
            skills=["Python", "JavaScript", "Docker"],
            experience=[
                {
                    "company": "Tech Corp",
                    "position": "Developer",
                    "start_date": "2020-01-01",
                    "end_date": "2023-01-01",
                    "description": "Developed applications"
                }
            ],
            education=[
                {
                    "institution": "University",
                    "degree": "Bachelor of Science",
                    "field_of_study": "Computer Science",
                    "graduation_year": 2019
                }
            ],
            performance_history={
                "rating": 4.5,
                "projects": 10
            }
        )
        
        assert len(resume_data.skills) == 3
        assert len(resume_data.experience) == 1
        assert len(resume_data.education) == 1
        assert resume_data.performance_history["rating"] == 4.5
