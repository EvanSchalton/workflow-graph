"""
Add a required skill to a job description.
Business logic function for adding skills to job descriptions.
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.job_description import JobDescription


async def add_skill_to_job_description(
    session: AsyncSession,
    job_id: int,
    skill: str
) -> Optional[JobDescription]:
    """
    Add a required skill to a job description.
    
    Args:
        session: Database session
        job_id: ID of the job description
        skill: Skill to add
        
    Returns:
        Updated JobDescription object if found, None otherwise
    """
    try:
        # Set search path to test schema
        await session.execute(text("SET search_path TO test"))
        
        # Import here to avoid circular imports
        from .get_job_description import get_job_description
        
        # Get the existing job description
        job = await get_job_description(session, job_id)
        if not job:
            return None
        
        # Check if the skill already exists in required_skills (case insensitive)
        skill_exists = False
        for existing_skill in job.required_skills:
            if existing_skill.lower() == skill.lower():
                skill_exists = True
                break
        
        # Only add the skill if it's not already present
        if not skill_exists:
            # For JSONB arrays, we need to use PostgreSQL's jsonb_array_append function
            sql = """
            UPDATE job_descriptions
            SET 
                required_skills = CASE 
                    WHEN required_skills IS NULL THEN CAST(:new_array AS jsonb)
                    ELSE required_skills || CAST(:new_skill AS jsonb)
                END,
                updated_at = :updated_at
            WHERE id = :job_id
            """
            
            params = {
                'job_id': job_id,
                'new_skill': f'"{skill.strip()}"',
                'new_array': f'["{skill.strip()}"]',
                'updated_at': datetime.utcnow()
            }
            
            # Execute the update
            await session.execute(text(sql), params)
            await session.commit()
        
        # Get the updated job description
        return await get_job_description(session, job_id)
        
    except Exception as e:
        print(f"Error in add_skill_to_job_description: {e}")
        import traceback
        traceback.print_exc()
        await session.rollback()
        return None
