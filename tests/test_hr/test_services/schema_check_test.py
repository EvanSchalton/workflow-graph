"""
Test to validate schema definitions match between SQLAlchemy models and the PostgreSQL database.
"""

import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from api.hr.models.job_description import JobDescription

# Use PostgreSQL for tests - with the existing "test" schema
DATABASE_URL = "postgresql+asyncpg://jira:jira@docker.lan:5432/postgres"


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


@pytest.mark.asyncio
async def test_job_description_schema(db_session: AsyncSession):
    """Test that the job_descriptions table has the correct structure."""
    # Execute a query to get information about the required_skills column
    result = await db_session.execute(
        text("""
        SELECT column_name, data_type, udt_name
        FROM information_schema.columns
        WHERE table_name = 'job_descriptions' AND column_name = 'required_skills'
        """)
    )
    
    # Fetch one row
    row = result.fetchone()
    
    # Print for debugging
    if row:
        column_name, data_type, udt_name = row
        print(f"\nPostgreSQL Database Column: {column_name}, Data Type: {data_type}, UDT: {udt_name}")
        
        # Check if the type is JSONB
        assert data_type.lower() == 'jsonb', f"Expected JSONB but got {data_type}"
        
        # Check the SQLAlchemy model definition
        from sqlalchemy.dialects.postgresql import ARRAY, JSONB
        
        print("\nSQLAlchemy model definition:")
        print(f"  Column type: {JobDescription.__table__.c.required_skills.type}")  # type: ignore
        print(f"  Is ARRAY? {isinstance(JobDescription.__table__.c.required_skills.type, ARRAY)}")  # type: ignore
        print(f"  Is JSONB? {isinstance(JobDescription.__table__.c.required_skills.type, JSONB)}")  # type: ignore
        
        # Verify that the model correctly uses JSONB
        assert isinstance(JobDescription.__table__.c.required_skills.type, JSONB), "JobDescription model should use JSONB for required_skills"  # type: ignore
        
        print("\n✅ Schema validation passed: Both model and database use JSONB for required_skills")
        
        # Also print the model's attributes for a more complete picture
        print("\nJobDescription model attributes:")
        for attr_name, attr_value in JobDescription.__annotations__.items():
            if attr_name == "required_skills":
                print(f"  {attr_name}: {attr_value}")
                print(f"  Field definition: {getattr(JobDescription, attr_name, None)}")
    else:
        assert False, "required_skills column not found in job_descriptions table"
