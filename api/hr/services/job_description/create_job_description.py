"""
Create a new job description.
Business logic function for creating job descriptions.
"""

from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.job_description import JobDescription, JobDescriptionCreate, ExperienceLevel


async def create_job_description(
    session: AsyncSession,
    job_data: JobDescriptionCreate
) -> JobDescription:
    """
    Create a new job description.
    
    Args:
        session: Database session
        job_data: New job description data
        
    Returns:
        Created JobDescription object
    """
    try:
        # Set search path to test schema
        await session.execute(text("SET search_path TO test"))
        
        # Normalize experience level - make sure it's an enum instance
        experience_level = job_data.experience_level
        if isinstance(experience_level, str):
            experience_level = ExperienceLevel(experience_level.lower())
            
        # Create job description instance
        job = JobDescription(
            title=job_data.title,
            description=job_data.description,
            required_skills=job_data.required_skills,
            experience_level=experience_level,
            department=job_data.department,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add to session and commit
        session.add(job)
        await session.commit()
        
        # Import here to avoid circular imports
        from .get_job_description import get_job_description
        
        # Get the job by ID using our get_job_description function
        # which is already handling JSONB data type correctly
        if job.id:
            # Return a freshly loaded instance that is properly initialized
            refreshed_job = await get_job_description(session, job.id)
            if refreshed_job:
                # Make sure experience_level is an ExperienceLevel enum, not a string
                if isinstance(refreshed_job.experience_level, str):
                    refreshed_job.experience_level = ExperienceLevel(refreshed_job.experience_level.lower())
                
                return refreshed_job
        
        return job
    except Exception as e:
        print(f"Error in create_job_description: {e}")
        import traceback
        traceback.print_exc()
        await session.rollback()
        raise
