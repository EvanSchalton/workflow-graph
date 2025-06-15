"""
Test skill and experience management for resume service.
"""
from uuid import uuid4
import pytest
from datetime import date
from sqlmodel.ext.asyncio.session import AsyncSession
from tests.utils import get_unique_test_id

from api.hr.services.resume import (
    create_resume, get_resume,
    add_skill_to_resume, remove_skill_from_resume,
    add_experience_to_resume, update_resume_experience,
    calculate_skill_match
)
from api.hr.models.resume import ResumeCreate


# Skill Management Tests

@pytest.mark.asyncio
async def test_add_skill_to_resume_success(test_session: AsyncSession, sample_resume_data: ResumeCreate) -> None:
    """Test successful skill addition."""
    resume = await create_resume(test_session, sample_resume_data)
    assert resume.id is not None, "Resume should have an ID after creation"
    initial_skills = resume.skills.copy()

    updated_resume = await add_skill_to_resume(test_session, resume.id, "Machine Learning")

    assert updated_resume is not None
    assert "Machine Learning" in updated_resume.skills
    assert len(updated_resume.skills) == len(initial_skills) + 1
    # Check that existing skills are preserved
    for skill in initial_skills:
        assert skill in updated_resume.skills


@pytest.mark.asyncio
async def test_add_skill_duplicate(test_session: AsyncSession, sample_resume_data: ResumeCreate) -> None:
    """Test adding duplicate skill (should not duplicate)."""
    resume = await create_resume(test_session, sample_resume_data)
    assert resume.id is not None, "Resume should have an ID after creation"
    existing_skill = resume.skills[0]
    initial_count = len(resume.skills)

    updated_resume = await add_skill_to_resume(test_session, resume.id, existing_skill)

    assert updated_resume is not None
    assert len(updated_resume.skills) == initial_count  # No new skill added
    assert updated_resume.skills.count(existing_skill) == 1  # No duplicate


@pytest.mark.asyncio
async def test_add_skill_case_insensitive(test_session: AsyncSession, sample_resume_data: ResumeCreate) -> None:
    """Test adding skill with different case (should not duplicate)."""
    resume = await create_resume(test_session, sample_resume_data)
    assert resume.id is not None, "Resume should have an ID after creation"
    if "Python" in resume.skills:
        existing_skill = "Python"
    else:
        # Add a skill first
        await add_skill_to_resume(test_session, resume.id, "Python")
        retrieved_resume = await get_resume(test_session, resume.id)
        assert retrieved_resume is not None, "Resume should be retrievable after creation"
        assert retrieved_resume.id is not None, "Retrieved resume should have an ID"
        resume = retrieved_resume
        existing_skill = "Python"

    initial_count = len(resume.skills)
    assert resume.id is not None, "Resume should have an ID before skill operation"

    # Try to add same skill with different case
    updated_resume = await add_skill_to_resume(test_session, resume.id, "python")

    assert updated_resume is not None
    assert len(updated_resume.skills) == initial_count  # No new skill added


@pytest.mark.asyncio
async def test_add_skill_empty_string(test_session: AsyncSession, sample_resume_data: ResumeCreate) -> None:
    """Test adding empty skill raises ValueError."""
    resume = await create_resume(test_session, sample_resume_data)
    assert resume.id is not None, "Resume should have an ID after creation"

    with pytest.raises(ValueError, match="Skill cannot be empty"):
        await add_skill_to_resume(test_session, resume.id, "")


@pytest.mark.asyncio
async def test_add_skill_whitespace_only(test_session: AsyncSession, sample_resume_data: ResumeCreate) -> None:
    """Test adding whitespace-only skill raises ValueError."""
    resume = await create_resume(test_session, sample_resume_data)
    assert resume.id is not None, "Resume should have an ID after creation"

    with pytest.raises(ValueError, match="Skill cannot be empty"):
        await add_skill_to_resume(test_session, resume.id, "   ")


@pytest.mark.asyncio
async def test_add_skill_resume_not_found(test_session: AsyncSession) -> None:
    """Test adding skill to non-existent resume returns None."""
    result = await add_skill_to_resume(test_session, get_unique_test_id(), "Python")
    assert result is None


# Experience Management Tests

@pytest.mark.asyncio
async def test_add_experience_success(test_session: AsyncSession, sample_resume_data: ResumeCreate) -> None:
    """Test successful experience addition."""
    resume = await create_resume(test_session, sample_resume_data)
    assert resume.id is not None, "Resume should have an ID after creation"
    initial_count = len(resume.experience)

    new_experience = {
        "company": "New Company",
        "position": "Software Engineer",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "description": "Worked on exciting projects"
    }

    updated_resume = await add_experience_to_resume(test_session, resume.id, new_experience)

    assert updated_resume is not None
    assert len(updated_resume.experience) == initial_count + 1

    # Find the new experience
    added_exp = None
    for exp in updated_resume.experience:
        if exp["company"] == "New Company":
            added_exp = exp
            break

    assert added_exp is not None
    assert added_exp["position"] == "Software Engineer"
    assert added_exp["start_date"] == "2023-01-01"


# Skill Matching Tests

@pytest.mark.asyncio
async def test_calculate_skill_match_perfect_match(test_session: AsyncSession, sample_resume_data: ResumeCreate) -> None:
    """Test skill matching with perfect match."""
    resume = await create_resume(test_session, sample_resume_data)
    assert resume.id is not None, "Resume should have an ID after creation"
    required_skills = resume.skills.copy()  # Same skills as resume

    match_score = await calculate_skill_match(test_session, resume.id, required_skills)

    assert match_score == 1.0  # Perfect match


@pytest.mark.asyncio
async def test_calculate_skill_match_partial_match(test_session: AsyncSession, sample_resume_data: ResumeCreate) -> None:
    """Test skill matching with partial match."""
    resume = await create_resume(test_session, sample_resume_data)
    assert resume.id is not None, "Resume should have an ID after creation"

    # Mix of matching and non-matching skills
    required_skills = resume.skills[:1] + ["NonExistentSkill1", "NonExistentSkill2"]

    match_score = await calculate_skill_match(test_session, resume.id, required_skills)

    expected_score = 1.0 / len(required_skills)  # 1 match out of total required
    assert abs(match_score - expected_score) < 0.01  # Allow small floating point differences


@pytest.mark.asyncio
async def test_calculate_skill_match_no_match(test_session: AsyncSession, sample_resume_data: ResumeCreate) -> None:
    """Test skill matching with no matches."""
    
    # Use a different email to avoid conflicts with other tests
    modified_data = sample_resume_data.model_copy()
    unique_id = str(uuid4())[:8]
    modified_data.email = f"no-match-test-{unique_id}@example.com"
    
    resume = await create_resume(test_session, modified_data)
    assert resume.id is not None, "Resume should have an ID after creation"
    required_skills = ["NonExistentSkill1", "NonExistentSkill2"]

    match_score = await calculate_skill_match(test_session, resume.id, required_skills)

    assert match_score == 0.0  # No matches
