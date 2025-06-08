"""
Get a resume by ID.
Business logic function for retrieving a single resume.
"""

from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.resume import Resume


async def get_resume(
    session: AsyncSession,
    resume_id: int
) -> Optional[Resume]:
    """
    Get a resume by ID.
    
    Args:
        session: Database session
        resume_id: Resume ID to fetch
        
    Returns:
        Resume object if found, None otherwise
    """
    try:
        # Set search path to test schema
        await session.execute(text("SET search_path TO test"))
        
        # Execute query to get resume
        result = await session.execute(
            text("""
            SELECT id, name, email, phone, summary, skills, experience, 
                   education, performance_history, created_at, updated_at
            FROM resumes
            WHERE id = :resume_id
            """),
            {"resume_id": resume_id}
        )
        
        row = result.first()
        if not row:
            return None
        
        # Create Resume object from row data
        resume = Resume(
            id=row.id,
            name=row.name,
            email=row.email,
            phone=row.phone,
            summary=row.summary,
            skills=row.skills or [],
            experience=row.experience or [],
            education=row.education or [],
            performance_history=row.performance_history or {},
            created_at=row.created_at,
            updated_at=row.updated_at
        )
        
        return resume
        
    except Exception as e:
        print(f"Error in get_resume: {e}")
        import traceback
        traceback.print_exc()
        return None
