"""
Delete a resume.
Business logic function for deleting resumes.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def delete_resume(
    session: AsyncSession,
    resume_id: int
) -> bool:
    """
    Delete a resume by ID.
    
    Args:
        session: Database session
        resume_id: ID of resume to delete
        
    Returns:
        True if resume was deleted, False if not found
        
    Raises:
        Exception: For database errors
    """
    try:
        # Set search path to test schema
        await session.execute(text("SET search_path TO test"))
        
        # Check if resume exists
        from .get_resume import get_resume
        existing_resume = await get_resume(session, resume_id)
        if not existing_resume:
            return False
        
        # Delete the resume
        await session.execute(
            text("DELETE FROM resumes WHERE id = :resume_id"),
            {"resume_id": resume_id}
        )
        
        await session.commit()
        return True
        
    except Exception as e:
        print(f"Error in delete_resume: {e}")
        import traceback
        traceback.print_exc()
        await session.rollback()
        raise
