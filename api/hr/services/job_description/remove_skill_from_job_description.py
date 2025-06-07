"""
Remove a required skill from a job description.
Business logic function for removing skills from job descriptions.
"""

from typing import Optional
from datetime import datetime
import json
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.job_description import JobDescription


async def remove_skill_from_job_description(
    session: AsyncSession,
    job_id: int,
    skill: str
) -> Optional[JobDescription]:
    """
    Remove a required skill from a job description.
    
    Args:
        session: Database session
        job_id: ID of the job description
        skill: Skill to remove
        
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
            
        # Find the skill index in the array (case insensitive)
        remove_index = None
        new_skills = []
        
        for i, existing_skill in enumerate(job.required_skills):
            if existing_skill.lower() == skill.lower():
                remove_index = i
            else:
                new_skills.append(existing_skill)
        
        # Only update if the skill was found
        if remove_index is not None:
            # For JSONB, we need to create a new array without the removed skill
            sql = """
            UPDATE job_descriptions
            SET 
                required_skills = CAST(:new_skills AS jsonb),
                updated_at = :updated_at
            WHERE id = :job_id
            """
            
            params = {
                'job_id': job_id,
                'new_skills': json.dumps(new_skills),  # Convert list to JSON string
                'updated_at': datetime.utcnow()
            }
            
            # Execute the update
            await session.execute(text(sql), params)
            await session.commit()
        
        # Get the updated job description
        return await get_job_description(session, job_id)
            
    except Exception as e:
        print(f"Error in remove_skill_from_job_description: {e}")
        import traceback
        traceback.print_exc()
        await session.rollback()
        return None
