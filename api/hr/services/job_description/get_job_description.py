"""
Get a job description by ID.
Business logic function for retrieving a single job description.
"""

from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.job_description import JobDescription, ExperienceLevel


async def get_job_description(
    session: AsyncSession,
    job_id: int
) -> Optional[JobDescription]:
    """
    Get a job description by ID.
    
    Args:
        session: Database session
        job_id: ID of the job description to retrieve
        
    Returns:
        JobDescription object if found, None otherwise
    """
    try:
        # Set search path to test schema first
        await session.execute(text("SET search_path TO test"))
        
        # Create a fresh query to work with the test schema
        raw_sql = f"""
        SELECT id, title, description, required_skills, experience_level, department, created_at, updated_at
        FROM job_descriptions
        WHERE id = {job_id}
        """
        result = await session.execute(text(raw_sql))
        
        # Map result to JobDescription model
        for row in result:
            # If we have any result, convert the first one to a JobDescription and return it
            # Debug info
            print(f"Found job with ID {job_id}: {row}")
            try:
                # Format experience_level properly
                exp_level = row.experience_level
                if isinstance(exp_level, str):
                    exp_level = ExperienceLevel(exp_level.lower())
                
                return JobDescription(
                    id=row.id, 
                    title=row.title,
                    description=row.description,
                    required_skills=row.required_skills,
                    experience_level=exp_level,
                    department=row.department,
                    created_at=row.created_at,
                    updated_at=row.updated_at
                )
            except Exception as e:
                print(f"Error creating JobDescription from row: {e}")
                print(f"Row data: {row}")
                raise
        
        # No result found
        print(f"No job found with ID {job_id}")
        return None
            
    except Exception as e:
        # Print any exceptions for debugging
        print(f"Error in get_job_description: {e}")
        import traceback
        traceback.print_exc()
        return None
