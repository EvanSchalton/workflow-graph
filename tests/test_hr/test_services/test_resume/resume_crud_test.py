"""
Comprehensive tests for resume CRUD operations.
"""
from uuid import UUID
import pytest
from typing import Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from tests.utils import get_unique_test_id
from api.hr.models.resume import Resume, ResumeCreate
from api.hr.services.resume import (
    create_resume,
    get_resume,
    get_resumes,
    update_resume,
    delete_resume
)


# Resume Creation Tests

@pytest.mark.asyncio
async def test_create_resume_success(test_session: AsyncSession, sample_resume_data: ResumeCreate) -> None:
    """Test successful resume creation."""
    resume = await create_resume(test_session, sample_resume_data)

    assert resume is not None
    assert isinstance(resume, Resume)
    assert resume.id is not None
    assert resume.email == sample_resume_data.email
    assert resume.name == sample_resume_data.name
    assert resume.skills == sample_resume_data.skills
    assert len(resume.experience) == len(sample_resume_data.experience)
    assert len(resume.education) == len(sample_resume_data.education)


@pytest.mark.asyncio
async def test_create_resume_duplicate_email(test_session, sample_resume_data):
    """Test that duplicate email raises ValueError."""
    # Create first resume
    await create_resume(test_session, sample_resume_data)

    # Try to create second resume with same email
    duplicate_data = ResumeCreate(
        name="Different Name",
        email=sample_resume_data.email,  # Same email
        phone=sample_resume_data.phone,
        skills=sample_resume_data.skills,
        experience=sample_resume_data.experience,
        education=sample_resume_data.education
    )

    with pytest.raises(ValueError, match=".*email already exists"):
        await create_resume(test_session, duplicate_data)


@pytest.mark.asyncio
async def test_create_resume_invalid_email(test_session, sample_resume_data):
    """Test that invalid email raises ValueError."""
    invalid_data = ResumeCreate(
        name=sample_resume_data.name,
        email="invalid-email",  # Invalid email
        phone=sample_resume_data.phone,
        skills=sample_resume_data.skills,
        experience=sample_resume_data.experience,
        education=sample_resume_data.education
    )

    with pytest.raises(ValueError, match="Invalid email format"):
        await create_resume(test_session, invalid_data)


@pytest.mark.asyncio
async def test_create_resume_missing_required_fields(test_session):
    """Test that missing required fields raises ValueError."""
    with pytest.raises(ValueError, match="Email is required"):
        await create_resume(test_session, {})


@pytest.mark.asyncio
async def test_create_resume_future_experience_dates(test_session, sample_resume_data):
    """Test that future experience dates raise ValueError."""
    future_experience = sample_resume_data.experience.copy()
    future_experience[0]["start_date"] = "2030-01-01"
    
    future_data = ResumeCreate(
        name=sample_resume_data.name,
        email=sample_resume_data.email,
        phone=sample_resume_data.phone,
        skills=sample_resume_data.skills,
        experience=future_experience,
        education=sample_resume_data.education
    )

    with pytest.raises(ValueError, match="Future dates not allowed"):
        await create_resume(test_session, future_data)


# Resume Reading Tests

@pytest.mark.asyncio
async def test_get_resume_success(test_session, sample_resume_data):
    """Test successful resume retrieval."""
    created_resume = await create_resume(test_session, sample_resume_data)
    
    retrieved_resume = await get_resume(test_session, created_resume.id)
    
    assert retrieved_resume is not None
    assert retrieved_resume.id == created_resume.id
    assert retrieved_resume.email == created_resume.email
    assert retrieved_resume.name == created_resume.name


@pytest.mark.asyncio
async def test_get_resume_not_found(test_session):
    """Test that get_resume returns None for non-existent ID."""
    non_existent_id = get_unique_test_id()
    resume = await get_resume(test_session, non_existent_id)
    assert resume is None


@pytest.mark.asyncio
async def test_get_resumes_empty(test_session):
    """Test get_resumes with no data."""
    resumes = await get_resumes(test_session)
    assert resumes == []


@pytest.mark.asyncio
async def test_get_resumes_with_data(test_session, sample_resume_data, test_uuid:str):
    """Test get_resumes with existing data."""
    # Create some test resumes
    await create_resume(test_session, sample_resume_data)
    
    # Create another resume with different email
    second_data = ResumeCreate(
        name="Jane Smith",
        email=f"jane.smith-{test_uuid}@example.com",
        phone="+1-555-0200",
        skills=["Java", "Spring", "Docker"],
        experience=[],
        education=[]
    )
    await create_resume(test_session, second_data)
    
    resumes = await get_resumes(test_session)
    assert len(resumes) == 2


# Resume Update Tests

@pytest.mark.asyncio
async def test_update_resume_success(test_session, sample_resume_data):
    """Test successful resume update."""
    created_resume = await create_resume(test_session, sample_resume_data)
    
    update_data = {
        "name": "Updated Name",
        "skills": ["Updated Skill"]
    }
    
    updated_resume = await update_resume(test_session, created_resume.id, update_data)
    
    assert updated_resume is not None
    assert updated_resume.name == "Updated Name"
    assert updated_resume.skills == ["Updated Skill"]
    # Email should remain unchanged
    assert updated_resume.email == sample_resume_data.email


@pytest.mark.asyncio
async def test_update_resume_not_found(test_session, test_uuid: str):
    """Test update with non-existent resume ID."""
    non_existent_id = int(UUID(test_uuid))
    update_data = {"name": test_uuid}
    
    result = await update_resume(test_session, non_existent_id, update_data)
    assert result is None


@pytest.mark.asyncio
async def test_update_resume_duplicate_email(test_session: AsyncSession, sample_resume_data: ResumeCreate, test_uuid: str) -> None:
    """Test that updating to existing email raises ValueError."""
    # Create first resume
    first_resume = await create_resume(test_session, sample_resume_data)
    assert first_resume.id is not None, "First resume should have an ID after creation"
    
    # Create second resume with different email
    second_data = ResumeCreate(
        name="Jane Smith",
        email=f"jane.smith-{test_uuid}@example.com",
        phone="+1-555-0200",
        skills=[],
        experience=[],
        education=[]
    )
    second_resume = await create_resume(test_session, second_data)
    assert second_resume.id is not None, "Second resume should have an ID after creation"
    
    # Try to update second resume to use first resume's email
    with pytest.raises(ValueError, match=".*email already exists"):
        await update_resume(test_session, second_resume.id, {"email": first_resume.email})


# Resume Deletion Tests

@pytest.mark.asyncio
async def test_delete_resume_success(test_session, sample_resume_data):
    """Test successful resume deletion."""
    created_resume = await create_resume(test_session, sample_resume_data)
    
    # Delete the resume
    success = await delete_resume(test_session, created_resume.id)
    assert success is True
    
    # Verify it's actually deleted
    deleted_resume = await get_resume(test_session, created_resume.id)
    assert deleted_resume is None


@pytest.mark.asyncio
async def test_delete_resume_not_found(test_session):
    """Test delete with non-existent resume ID."""
    non_existent_id = get_unique_test_id()
    success = await delete_resume(test_session, non_existent_id)
    assert success is False