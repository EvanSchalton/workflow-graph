"""
Test to validate schema definitions in SQLAlchemy models without requiring a database connection.

Following the development patterns document, this test validates model definitions
without attempting to connect to a real database, which could cause timeouts or
failures in environments where the database is not available.
"""

import pytest
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

from api.hr.models.job_description import JobDescription


def test_job_description_schema_type():
    """
    Verify that the job_description model is using the correct type for required_skills.
    
    This test directly checks the SQLAlchemy model definition rather than querying
    the database schema. This approach follows the development patterns document which
    discourages manual terminal testing and direct database queries in tests.
    """
    # Check the SQLAlchemy model definition directly
    print("\nSQLAlchemy model definition:")
    print(f"  Column type: {JobDescription.__table__.c.required_skills.type}")  # type: ignore
    print(f"  Is ARRAY? {isinstance(JobDescription.__table__.c.required_skills.type, ARRAY)}")  # type: ignore
    print(f"  Is JSONB? {isinstance(JobDescription.__table__.c.required_skills.type, JSONB)}")  # type: ignore
    
    # Verify that the model correctly uses JSONB
    assert isinstance(JobDescription.__table__.c.required_skills.type, JSONB), "JobDescription model should use JSONB for required_skills"  # type: ignore
    
    print("\n✅ Schema validation passed: Model uses JSONB for required_skills")
    
    # Also print the model's attributes for a more complete picture
    print("\nJobDescription model attributes:")
    for attr_name, attr_value in JobDescription.__annotations__.items():
        if attr_name == "required_skills":
            print(f"  {attr_name}: {attr_value}")
            print(f"  Field definition: {getattr(JobDescription, attr_name, None)}")
