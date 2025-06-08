"""
Test skill and experience management for resume service.
"""

import pytest
from datetime import date

from api.hr.services.resume import (
    create_resume, get_resume,
    add_skill_to_resume, remove_skill_from_resume,
    add_experience_to_resume, update_resume_experience,
    calculate_skill_match
)


class TestSkillManagement:
    """Test skill management functionality."""
    
    @pytest.mark.asyncio
    async def test_add_skill_to_resume_success(self, test_session, sample_resume_data):
        """Test successful skill addition."""
        resume = await create_resume(test_session, sample_resume_data)
        initial_skills = resume.skills.copy()

        updated_resume = await add_skill_to_resume(test_session, resume.id, "Machine Learning")

        assert updated_resume is not None
        assert "Machine Learning" in updated_resume.skills
        assert len(updated_resume.skills) == len(initial_skills) + 1
        # Check that existing skills are preserved
        for skill in initial_skills:
            assert skill in updated_resume.skills

    @pytest.mark.asyncio
    async def test_add_skill_duplicate(self, test_session, sample_resume_data):
        """Test adding duplicate skill (should not duplicate)."""
        resume = await create_resume(test_session, sample_resume_data)
        existing_skill = resume.skills[0]
        initial_count = len(resume.skills)

        updated_resume = await add_skill_to_resume(test_session, resume.id, existing_skill)

        assert updated_resume is not None
        assert len(updated_resume.skills) == initial_count  # No new skill added
        assert updated_resume.skills.count(existing_skill) == 1  # No duplicate

    @pytest.mark.asyncio
    async def test_add_skill_case_insensitive(self, test_session, sample_resume_data):
        """Test adding skill with different case (should not duplicate)."""
        resume = await create_resume(test_session, sample_resume_data)
        if "Python" in resume.skills:
            existing_skill = "Python"
        else:
            # Add a skill first
            await add_skill_to_resume(test_session, resume.id, "Python")
            resume = await get_resume(test_session, resume.id)
            existing_skill = "Python"

        initial_count = len(resume.skills)

        # Try to add same skill with different case
        updated_resume = await add_skill_to_resume(test_session, resume.id, "python")

        assert updated_resume is not None
        assert len(updated_resume.skills) == initial_count  # No new skill added

    @pytest.mark.asyncio
    async def test_add_skill_empty_string(self, test_session, sample_resume_data):
        """Test adding empty skill raises ValueError."""
        resume = await create_resume(test_session, sample_resume_data)

        with pytest.raises(ValueError, match="Skill cannot be empty"):
            await add_skill_to_resume(test_session, resume.id, "")

    @pytest.mark.asyncio
    async def test_add_skill_whitespace_only(self, test_session, sample_resume_data):
        """Test adding whitespace-only skill raises ValueError."""
        resume = await create_resume(test_session, sample_resume_data)

        with pytest.raises(ValueError, match="Skill cannot be empty"):
            await add_skill_to_resume(test_session, resume.id, "   ")

    @pytest.mark.asyncio
    async def test_add_skill_resume_not_found(self, test_session):
        """Test adding skill to non-existent resume returns None."""
        result = await add_skill_to_resume(test_session, 99999, "Python")
        assert result is None

    @pytest.mark.asyncio
    async def test_remove_skill_success(self, test_session, sample_resume_data):
        """Test successful skill removal."""
        resume = await create_resume(test_session, sample_resume_data)
        skill_to_remove = resume.skills[0]
        initial_count = len(resume.skills)

        updated_resume = await remove_skill_from_resume(test_session, resume.id, skill_to_remove)

        assert updated_resume is not None
        assert skill_to_remove not in updated_resume.skills
        assert len(updated_resume.skills) == initial_count - 1

    @pytest.mark.asyncio
    async def test_remove_skill_not_present(self, test_session, sample_resume_data):
        """Test removing non-existent skill (should not error)."""
        resume = await create_resume(test_session, sample_resume_data)
        initial_count = len(resume.skills)

        updated_resume = await remove_skill_from_resume(test_session, resume.id, "NonExistentSkill")

        assert updated_resume is not None
        assert len(updated_resume.skills) == initial_count  # No change

    @pytest.mark.asyncio
    async def test_remove_skill_case_insensitive(self, test_session, sample_resume_data):
        """Test removing skill with different case."""
        resume = await create_resume(test_session, sample_resume_data)
        # Ensure we have a Python skill
        if "Python" not in resume.skills:
            await add_skill_to_resume(test_session, resume.id, "Python")
            resume = await get_resume(test_session, resume.id)

        initial_count = len(resume.skills)

        # Remove with different case
        updated_resume = await remove_skill_from_resume(test_session, resume.id, "python")

        assert updated_resume is not None
        assert "Python" not in updated_resume.skills
        assert len(updated_resume.skills) == initial_count - 1

    @pytest.mark.asyncio
    async def test_remove_skill_resume_not_found(self, test_session):
        """Test removing skill from non-existent resume returns None."""
        result = await remove_skill_from_resume(test_session, 99999, "Python")
        assert result is None


class TestExperienceManagement:
    """Test experience management functionality."""

    @pytest.mark.asyncio
    async def test_add_experience_success(self, test_session, sample_resume_data):
        """Test successful experience addition."""
        resume = await create_resume(test_session, sample_resume_data)
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

    @pytest.mark.asyncio
    async def test_add_experience_future_dates(self, test_session, sample_resume_data):
        """Test adding experience with future dates raises ValueError."""
        resume = await create_resume(test_session, sample_resume_data)

        future_experience = {
            "company": "Future Company",
            "position": "Time Traveler",
            "start_date": "2030-01-01",
            "end_date": "2030-12-31"
        }

        with pytest.raises(ValueError, match="cannot be in the future"):
            await add_experience_to_resume(test_session, resume.id, future_experience)

    @pytest.mark.asyncio
    async def test_add_experience_end_before_start(self, test_session, sample_resume_data):
        """Test adding experience with end date before start date raises ValueError."""
        resume = await create_resume(test_session, sample_resume_data)

        invalid_experience = {
            "company": "Invalid Company",
            "position": "Time Traveler",
            "start_date": "2023-12-31",
            "end_date": "2023-01-01"
        }

        with pytest.raises(ValueError, match="End date cannot be before start date"):
            await add_experience_to_resume(test_session, resume.id, invalid_experience)

    @pytest.mark.asyncio
    async def test_add_experience_resume_not_found(self, test_session):
        """Test adding experience to non-existent resume returns None."""
        experience = {
            "company": "Test Company",
            "position": "Developer",
            "start_date": "2023-01-01"
        }

        result = await add_experience_to_resume(test_session, 99999, experience)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_resume_experience_success(self, test_session, sample_resume_data):
        """Test successful experience update."""
        resume = await create_resume(test_session, sample_resume_data)

        new_experiences = [
            {
                "company": "Updated Company 1",
                "position": "Senior Developer",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31"
            },
            {
                "company": "Updated Company 2",
                "position": "Lead Developer",
                "start_date": "2022-01-01",
                "end_date": "2022-12-31"
            }
        ]

        updated_resume = await update_resume_experience(test_session, resume.id, new_experiences)

        assert updated_resume is not None
        assert len(updated_resume.experience) == 2
        assert updated_resume.experience[0]["company"] == "Updated Company 1"
        assert updated_resume.experience[1]["company"] == "Updated Company 2"

    @pytest.mark.asyncio
    async def test_update_resume_experience_empty_list(self, test_session, sample_resume_data):
        """Test updating experience with empty list clears experience."""
        resume = await create_resume(test_session, sample_resume_data)

        updated_resume = await update_resume_experience(test_session, resume.id, [])

        assert updated_resume is not None
        assert len(updated_resume.experience) == 0

    @pytest.mark.asyncio
    async def test_update_resume_experience_not_found(self, test_session):
        """Test updating experience for non-existent resume returns None."""
        result = await update_resume_experience(test_session, 99999, [])
        assert result is None


class TestSkillMatching:
    """Test skill matching functionality."""

    @pytest.mark.asyncio
    async def test_calculate_skill_match_perfect_match(self, test_session, sample_resume_data):
        """Test skill matching with perfect match."""
        resume = await create_resume(test_session, sample_resume_data)
        required_skills = resume.skills.copy()  # Same skills as resume

        match_score = await calculate_skill_match(test_session, resume.id, required_skills)

        assert match_score == 1.0  # Perfect match

    @pytest.mark.asyncio
    async def test_calculate_skill_match_partial_match(self, test_session, sample_resume_data):
        """Test skill matching with partial match."""
        resume = await create_resume(test_session, sample_resume_data)

        # Mix of matching and non-matching skills
        required_skills = resume.skills[:1] + ["NonExistentSkill1", "NonExistentSkill2"]

        match_score = await calculate_skill_match(test_session, resume.id, required_skills)

        expected_score = 1.0 / len(required_skills)  # 1 match out of total required
        assert abs(match_score - expected_score) < 0.01  # Allow small floating point differences

    @pytest.mark.asyncio
    async def test_calculate_skill_match_no_match(self, test_session, sample_resume_data):
        """Test skill matching with no matches."""
        # Use a different email to avoid conflicts with other tests
        modified_data = sample_resume_data.copy()
        modified_data.email = f"no-match-test-{modified_data.email}"
        
        resume = await create_resume(test_session, modified_data)
        required_skills = ["NonExistentSkill1", "NonExistentSkill2"]

        match_score = await calculate_skill_match(test_session, resume.id, required_skills)

        assert match_score == 0.0  # No matches

    @pytest.mark.asyncio
    async def test_calculate_skill_match_empty_required(self, test_session, sample_resume_data):
        """Test skill matching with empty required skills."""
        # Use a different email to avoid conflicts with other tests
        modified_data = sample_resume_data.copy()
        modified_data.email = f"empty-required-test-{modified_data.email}"
        
        resume = await create_resume(test_session, modified_data)

        match_score = await calculate_skill_match(test_session, resume.id, [])

        assert match_score == 1.0  # Empty requirements should return perfect match

    @pytest.mark.asyncio
    async def test_calculate_skill_match_case_insensitive(self, test_session, sample_resume_data):
        """Test skill matching is case insensitive."""
        resume = await create_resume(test_session, sample_resume_data)

        # Ensure we have a Python skill
        if "Python" not in resume.skills:
            await add_skill_to_resume(test_session, resume.id, "Python")

        required_skills = ["python", "JAVASCRIPT"]  # Different cases

        match_score = await calculate_skill_match(test_session, resume.id, required_skills)

        # Should match at least Python (case insensitive)
        assert match_score > 0.0

    @pytest.mark.asyncio
    async def test_calculate_skill_match_resume_not_found(self, test_session):
        """Test skill matching for non-existent resume returns 0."""
        match_score = await calculate_skill_match(test_session, 99999, ["Python"])
        assert match_score == 0.0
