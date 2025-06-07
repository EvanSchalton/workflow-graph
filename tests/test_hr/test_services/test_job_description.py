"""
Tests for job description service CRUD operations.
"""

import pytest
import pytest_asyncio
from datetime import datetime
from typing import List, Dict, Any, AsyncGenerator, Callable, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import Column, String, Text, text
from sqlmodel import SQLModel, Field

from api.hr.models.job_description import (
    ExperienceLevel,
    JobDescriptionCreate,
    JobDescriptionUpdate
)
from api.hr.services.job_description import (
    get_job_description,
    get_job_descriptions,
    create_job_description,
    update_job_description,
    delete_job_description,
    add_skill_to_job_description,
    remove_skill_from_job_description,
    find_matching_job_descriptions
)

# Use PostgreSQL for tests - with the existing "test" schema
DATABASE_URL = "postgresql+asyncpg://jira:jira@docker.lan:5432/postgres"

# Import the actual model - no need for a SQLite workaround
from api.hr.models.job_description import JobDescription


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session using the existing PostgreSQL test schema."""
    # Use PostgreSQL without specifying schema in URL
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        future=True,
        poolclass=NullPool,
    )
    
    # Create tables in the test schema
    async with engine.begin() as conn:
        await conn.execute(text('CREATE SCHEMA IF NOT EXISTS test'))
        await conn.execute(text('SET search_path TO test'))
        # Drop and recreate tables to ensure schema changes are applied
        await conn.execute(text('DROP TABLE IF EXISTS job_applications CASCADE'))
        await conn.execute(text('DROP TABLE IF EXISTS agents CASCADE'))
        await conn.execute(text('DROP TABLE IF EXISTS job_descriptions CASCADE'))
        # Create tables from the current models
        await conn.run_sync(SQLModel.metadata.create_all)
    
    # Create session
    async_session = async_sessionmaker(
        engine, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Set search path for this session
        await session.execute(text('SET search_path TO test'))
        yield session
    
    # Clean up: just truncate tables instead of dropping the schema
    async with engine.begin() as conn:
        await conn.execute(text('SET search_path TO test'))
        await conn.execute(text('TRUNCATE TABLE job_descriptions CASCADE'))
    
    await engine.dispose()


@pytest.fixture
def test_uuid() -> str:
    """Generate a unique ID for test traceability."""
    return str(uuid.uuid4())


@pytest_asyncio.fixture
async def job_description_factory(db_session: AsyncSession, test_uuid: str):
    """Factory fixture to create test job descriptions."""
    async def _create_job_description(
        title: str = "Test Job",
        description: str = "Test Description",
        required_skills: Optional[List[str]] = None,
        experience_level: ExperienceLevel = ExperienceLevel.JUNIOR,
        department: str = "Engineering"
    ) -> Any:  # Return Any type to avoid type conflicts
        # Add test_uuid for traceability
        traceable_title = f"{title} ({test_uuid})"
        traceable_description = f"{description} - Test ID: {test_uuid}"
        
        if required_skills is None:
            required_skills = ["Python", "FastAPI", "SQLAlchemy"]
        
        job_data = JobDescriptionCreate(
            title=traceable_title,
            description=traceable_description,
            required_skills=required_skills,
            experience_level=experience_level,
            department=department
        )
        return await create_job_description(db_session, job_data)
    
    return _create_job_description


@pytest.mark.asyncio
async def test_create_job_description(db_session: AsyncSession, test_uuid: str):
    """Test creating a new job description."""
    # Arrange
    job_data = JobDescriptionCreate(
        title=f"Software Engineer ({test_uuid})",
        description=f"Python developer position - Test ID: {test_uuid}",
        required_skills=["Python", "FastAPI", "SQLAlchemy"],
        experience_level=ExperienceLevel.MID,
        department="Engineering"
    )
    
    # Act
    job = await create_job_description(db_session, job_data)
    
    # Assert
    assert job.id is not None
    assert job.title == job_data.title
    assert job.description == job_data.description
    assert job.required_skills == job_data.required_skills
    assert job.experience_level == job_data.experience_level
    assert job.department == job_data.department
    assert isinstance(job.created_at, datetime)
    assert isinstance(job.updated_at, datetime)


@pytest.mark.asyncio
async def test_get_job_description(
    db_session: AsyncSession, job_description_factory
):
    """Test retrieving a job description by ID."""
    # Arrange
    created_job = await job_description_factory()
    
    # Act
    retrieved_job = await get_job_description(db_session, created_job.id)
    
    # Assert
    assert retrieved_job is not None
    assert retrieved_job.id == created_job.id
    assert retrieved_job.title == created_job.title


@pytest.mark.asyncio
async def test_get_job_description_not_found(db_session: AsyncSession):
    """Test retrieving a non-existent job description."""
    # Act
    job = await get_job_description(db_session, 999)
    
    # Assert
    assert job is None


@pytest.mark.asyncio
async def test_get_job_descriptions(
    db_session: AsyncSession, job_description_factory
):
    """Test retrieving multiple job descriptions."""
    # Arrange
    await job_description_factory(title="Job 1")
    await job_description_factory(title="Job 2")
    await job_description_factory(title="Job 3")
    
    # Act
    jobs = await get_job_descriptions(db_session)
    
    # Assert
    assert len(jobs) == 3


@pytest.mark.asyncio
async def test_get_job_descriptions_with_pagination(
    db_session: AsyncSession, job_description_factory
):
    """Test retrieving job descriptions with pagination."""
    # Arrange
    for i in range(10):
        await job_description_factory(title=f"Job {i+1}")
    
    # Act
    jobs = await get_job_descriptions(db_session, skip=2, limit=3)
    
    # Assert
    assert len(jobs) == 3


@pytest.mark.asyncio
async def test_get_job_descriptions_with_filters(
    db_session: AsyncSession, job_description_factory
):
    """Test retrieving job descriptions with filters."""
    # Arrange
    await job_description_factory(
        title="Frontend Developer",
        department="Engineering",
        experience_level=ExperienceLevel.JUNIOR,
        required_skills=["JavaScript", "React", "CSS"]
    )
    await job_description_factory(
        title="Backend Developer",
        department="Engineering",
        experience_level=ExperienceLevel.SENIOR,
        required_skills=["Python", "FastAPI", "PostgreSQL"]
    )
    await job_description_factory(
        title="Product Manager",
        department="Product",
        experience_level=ExperienceLevel.MID,
        required_skills=["Agile", "Roadmapping"]
    )
    
    # Test filtering by department
    department_jobs = await get_job_descriptions(
        db_session,
        filters={"department": "Engineering"}
    )
    
    assert len(department_jobs) == 2
    assert all(job.department == "Engineering" for job in department_jobs)
    
    # Test filtering by skill
    skill_jobs = await get_job_descriptions(
        db_session,
        filters={"skill": "python"}
    )
    
    assert len(skill_jobs) == 1
    assert skill_jobs[0].title.startswith("Backend Developer")
    assert "Python" in skill_jobs[0].required_skills
    
    # Test filtering by title
    title_jobs = await get_job_descriptions(
        db_session,
        filters={"title": "backend"}
    )
    
    assert len(title_jobs) == 1
    assert "Backend" in title_jobs[0].title


@pytest.mark.asyncio
async def test_update_job_description(
    db_session: AsyncSession, job_description_factory
):
    """Test updating a job description."""
    # Arrange
    job = await job_description_factory()
    update_data = JobDescriptionUpdate(
        title="Updated Job Title",
        description="Updated description"
    )
    
    # Act
    updated_job = await update_job_description(db_session, job.id, update_data)
    
    # Assert
    assert updated_job is not None
    assert updated_job.id == job.id
    assert updated_job.title == "Updated Job Title"
    assert updated_job.description == "Updated description"
    # Fields not included in the update should remain unchanged
    assert updated_job.department == job.department
    assert updated_job.experience_level == job.experience_level


@pytest.mark.asyncio
async def test_update_job_description_not_found(db_session: AsyncSession):
    """Test updating a non-existent job description."""
    # Arrange
    update_data = JobDescriptionUpdate(title="Updated Job Title")
    
    # Act
    updated_job = await update_job_description(db_session, 999, update_data)
    
    # Assert
    assert updated_job is None


@pytest.mark.asyncio
async def test_delete_job_description(
    db_session: AsyncSession, job_description_factory
):
    """Test deleting a job description."""
    # Arrange
    job = await job_description_factory()
    
    # Act
    result = await delete_job_description(db_session, job.id)
    
    # Assert
    assert result is True
    deleted_job = await get_job_description(db_session, job.id)
    assert deleted_job is None


@pytest.mark.asyncio
async def test_delete_job_description_not_found(db_session: AsyncSession):
    """Test deleting a non-existent job description."""
    # Act
    result = await delete_job_description(db_session, 999)
    
    # Assert
    assert result is False


@pytest.mark.asyncio
async def test_add_skill_to_job_description(
    db_session: AsyncSession, job_description_factory
):
    """Test adding a skill to a job description."""
    # Arrange
    job = await job_description_factory(required_skills=["Python", "FastAPI"])
    
    # Act
    updated_job = await add_skill_to_job_description(db_session, job.id, "SQLAlchemy")
    
    # Assert
    assert updated_job is not None
    assert "SQLAlchemy" in updated_job.required_skills
    assert len(updated_job.required_skills) == 3


@pytest.mark.asyncio
async def test_add_duplicate_skill_to_job_description(
    db_session: AsyncSession, job_description_factory
):
    """Test adding a duplicate skill to a job description."""
    # Arrange
    job = await job_description_factory(required_skills=["Python", "FastAPI"])
    
    # Act
    updated_job = await add_skill_to_job_description(db_session, job.id, "python")  # Case insensitive
    
    # Assert
    assert updated_job is not None
    assert len(updated_job.required_skills) == 2  # No duplicate added


@pytest.mark.asyncio
async def test_remove_skill_from_job_description(
    db_session: AsyncSession, job_description_factory
):
    """Test removing a skill from a job description."""
    # Arrange
    job = await job_description_factory(required_skills=["Python", "FastAPI", "SQLAlchemy"])
    
    # Act
    updated_job = await remove_skill_from_job_description(db_session, job.id, "FastAPI")
    
    # Assert
    assert updated_job is not None
    assert "FastAPI" not in updated_job.required_skills
    assert len(updated_job.required_skills) == 2


@pytest.mark.asyncio
async def test_remove_nonexistent_skill_from_job_description(
    db_session: AsyncSession, job_description_factory
):
    """Test removing a non-existent skill from a job description."""
    # Arrange
    job = await job_description_factory(required_skills=["Python", "FastAPI"])
    
    # Act
    updated_job = await remove_skill_from_job_description(db_session, job.id, "JavaScript")
    
    # Assert
    assert updated_job is not None
    assert len(updated_job.required_skills) == 2  # No change


@pytest.mark.asyncio
async def test_find_matching_job_descriptions(
    db_session: AsyncSession, job_description_factory
):
    """Test finding job descriptions that match given skills."""
    # Arrange
    await job_description_factory(
        title="Backend Developer",
        required_skills=["Python", "FastAPI", "PostgreSQL"],
        experience_level=ExperienceLevel.MID
    )
    await job_description_factory(
        title="Frontend Developer",
        required_skills=["JavaScript", "React", "CSS"],
        experience_level=ExperienceLevel.JUNIOR
    )
    await job_description_factory(
        title="Full Stack Developer",
        required_skills=["Python", "JavaScript", "React", "FastAPI"],
        experience_level=ExperienceLevel.SENIOR
    )
    
    # Act
    matches = await find_matching_job_descriptions(
        db_session,
        skills=["Python", "JavaScript", "Docker"]
    )
    
    # Assert
    assert len(matches) == 3  # All should match to some degree
    # Full Stack should be the best match
    assert "Full Stack Developer" in matches[0]["job"].title
    assert matches[0]["match_score"] >= matches[1]["match_score"]


@pytest.mark.asyncio
async def test_find_matching_job_descriptions_with_filters(
    db_session: AsyncSession, job_description_factory
):
    """Test finding job descriptions with experience level and department filters."""
    # Arrange
    await job_description_factory(
        title="Junior Backend Developer",
        required_skills=["Python", "FastAPI"],
        experience_level=ExperienceLevel.JUNIOR,
        department="Engineering"
    )
    await job_description_factory(
        title="Senior Backend Developer",
        required_skills=["Python", "FastAPI", "Architecture"],
        experience_level=ExperienceLevel.SENIOR,
        department="Engineering"
    )
    await job_description_factory(
        title="Data Scientist",
        required_skills=["Python", "Statistics", "ML"],
        experience_level=ExperienceLevel.MID,
        department="Data Science"
    )
    
    # Act
    matches = await find_matching_job_descriptions(
        db_session,
        skills=["Python", "Data Analysis"],
        experience_level=ExperienceLevel.MID,
        department="Data Science"
    )
    
    # Assert
    assert len(matches) == 1
    assert "Data Scientist" in matches[0]["job"].title
    assert matches[0]["job"].department == "Data Science"
    assert matches[0]["job"].experience_level == ExperienceLevel.MID
