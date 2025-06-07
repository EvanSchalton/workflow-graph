"""
Test to validate schema definitions match between SQLAlchemy models and the PostgreSQL database.
"""

import pytest
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.hr.models.job_description import JobDescription

# Import the db_session fixture from the main test file
from tests.test_hr.test_services.test_job_description import db_session


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
        from sqlalchemy import String
        
        print(f"\nSQLAlchemy model definition:")
        print(f"  Column type: {JobDescription.__table__.c.required_skills.type}")
        print(f"  Is ARRAY? {isinstance(JobDescription.__table__.c.required_skills.type, ARRAY)}")
        print(f"  Is JSONB? {isinstance(JobDescription.__table__.c.required_skills.type, JSONB)}")
        
        # We're expecting a mismatch - the model uses ARRAY(String) but the database uses JSONB
        # This is the core issue we need to fix

        # Also print the model's attributes for a more complete picture
        print("\nJobDescription model attributes:")
        for attr_name, attr_value in JobDescription.__annotations__.items():
            if attr_name == "required_skills":
                print(f"  {attr_name}: {attr_value}")
                print(f"  Field definition: {getattr(JobDescription, attr_name, None)}")
    else:
        assert False, "required_skills column not found in job_descriptions table"
