"""
Add a skill to a resume.
Business logic function for skill management.
"""

from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.resume import Resume


async def add_skill_to_resume(
    session: AsyncSession,
    resume_id: int,
    skill: str
) -> Optional[Resume]:
    """
    Add a skill to a resume if not already present.
    
    Args:
        session: Database session
        resume_id: Resume ID to update
        skill: Skill to add
        
    Returns:
        Updated Resume object if successful, None if resume not found
        
    Raises:
        ValueError: If skill is empty or invalid
        Exception: For database errors
    """
    try:
        # Validate skill
        if not skill or not skill.strip():
            raise ValueError("Skill cannot be empty")
        
        skill = skill.strip()
        
        # Set search path to test schema
        await session.execute(text("SET search_path TO test"))
        
        # Get current resume
        from .get_resume import get_resume
        resume = await get_resume(session, resume_id)
        if not resume:
            return None
        
        # Check if skill already exists (case-insensitive)
        if resume.has_skill(skill):
            return resume  # Skill already exists, no change needed
        
        # Add skill to the array using PostgreSQL array_append
        await session.execute(
            text("""
            UPDATE resumes 
            SET skills = array_append(skills, :skill),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :resume_id
            """),
            {"resume_id": resume_id, "skill": skill}
        )
        
        await session.commit()
        
        # Return updated resume
        updated_resume = await get_resume(session, resume_id)
        return updated_resume
        
    except ValueError:
        # Re-raise validation errors without rollback
        raise
    except Exception as e:
        print(f"Error in add_skill_to_resume: {e}")
        import traceback
        traceback.print_exc()
        await session.rollback()
        raise
