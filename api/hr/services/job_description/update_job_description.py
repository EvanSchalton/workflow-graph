"""
Update an existing job description.
Business logic function for updating job descriptions.
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.job_description import JobDescription, JobDescriptionUpdate, ExperienceLevel


async def update_job_description(
    session: AsyncSession,
    job_id: int,
    job_data: JobDescriptionUpdate
) -> Optional[JobDescription]:
    """
    Update an existing job description.
    
    Args:
        session: Database session
        job_id: ID of the job description to update
        job_data: Updated job description data
        
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
        
        # Prepare update data, excluding None values
        update_data = job_data.model_dump(exclude_unset=True)
        if not update_data:
            # No valid update data provided
            return job
        
        # Fix experience_level if it's in the update data
        if 'experience_level' in update_data:
            if isinstance(update_data['experience_level'], str):
                # Convert string to enum if needed
                update_data['experience_level'] = ExperienceLevel(update_data['experience_level'].lower())
            elif hasattr(update_data['experience_level'], 'value'):
                # Use the enum value
                update_data['experience_level'] = update_data['experience_level'].value
        
        # Always update the updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        # Build SQL update statement for JSONB compatibility
        set_clauses = []
        params = {'job_id': job_id}
        
        for key, value in update_data.items():
            if key == 'required_skills':
                # Handle JSONB type
                set_clauses.append("required_skills = CAST(:required_skills AS jsonb)")
                params['required_skills'] = value
            else:
                set_clauses.append(f"{key} = :{key}")
                params[key] = value
        
        sql = f"""
        UPDATE job_descriptions 
        SET {', '.join(set_clauses)}
        WHERE id = :job_id
        """
        
        # Execute the update
        await session.execute(text(sql), params)
        await session.commit()
        
        # Get the updated job description
        return await get_job_description(session, job_id)
    except Exception as e:
        print(f"Error in update_job_description: {e}")
        import traceback
        traceback.print_exc()
        await session.rollback()
        return None
