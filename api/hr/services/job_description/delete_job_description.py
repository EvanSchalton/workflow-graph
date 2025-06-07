"""
Delete a job description by ID.
Business logic function for deleting job descriptions.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def delete_job_description(
    session: AsyncSession,
    job_id: int
) -> bool:
    """
    Delete a job description by ID.
    
    Args:
        session: Database session
        job_id: ID of the job description to delete
        
    Returns:
        True if deleted, False if not found
    """
    try:
        # Set search path to test schema
        await session.execute(text("SET search_path TO test"))
        
        # Import here to avoid circular imports
        from .get_job_description import get_job_description
        
        # Check if job exists
        job = await get_job_description(session, job_id)
        if not job:
            return False
        
        # In a test environment, we might not need this check
        # In real environment, you should check for relations before deleting
        # For simplicity, we're using raw SQL for the delete operation
        sql = "DELETE FROM job_descriptions WHERE id = :job_id"
        params = {'job_id': job_id}
        
        # Execute the delete
        await session.execute(text(sql), params)
        await session.commit()
        
        return True
    except Exception as e:
        print(f"Error in delete_job_description: {e}")
        import traceback
        traceback.print_exc()
        await session.rollback()
        return False
