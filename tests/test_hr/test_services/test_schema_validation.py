"""
Test to validate schema definitions match between SQLAlchemy models and the PostgreSQL database.
"""

import pytest
import pytest_asyncio
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

# Use the same database URL as the other tests
DATABASE_URL = "postgresql+asyncpg://jira:jira@docker.lan:5432/postgres"


@pytest_asyncio.fixture
async def db_connection():
    """Create a test database connection."""
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        future=True,
        poolclass=NullPool,
    )
    
    async_session = async_sessionmaker(
        engine, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()


@pytest.mark.asyncio
async def test_job_description_schema(db_connection: AsyncSession):
    """Verify that the job_description table schema in PostgreSQL matches our model definition."""
    # Get the inspector using the connection from the session
    def get_inspector_and_columns(sync_session):
        # Get the connection from the session
        connection = sync_session.connection()
        inspector = inspect(connection)
        columns = inspector.get_columns("job_descriptions")
        return columns
    
    # Get the columns of the job_descriptions table
    columns = await db_connection.run_sync(get_inspector_and_columns)
    
    # Find the required_skills column
    required_skills_column = next(
        (column for column in columns if column["name"] == "required_skills"), 
        None
    )
    
    # Assert that the column exists
    assert required_skills_column is not None, "required_skills column not found in job_descriptions table"
    
    # Print the column type for debugging
    print(f"Type of required_skills column: {required_skills_column['type']}")
    
    # Get the type name as a string
    type_name = str(required_skills_column["type"])
    
    # Verify it's JSONB and not ARRAY
    assert "JSONB" in type_name.upper(), f"expected JSONB type but got {type_name}"
