"""
Calculate skill match score between resume and job requirements.
Business logic function for resume evaluation.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.resume import Resume


async def calculate_skill_match(
    session: AsyncSession,
    resume_id: int,
    required_skills: List[str]
) -> float:
    """
    Calculate how well a resume matches required skills.
    
    Args:
        session: Database session
        resume_id: Resume ID to evaluate
        required_skills: List of skills required for a position
        
    Returns:
        Skill match score between 0.0 and 1.0, or 0.0 if resume not found
        
    Raises:
        ValueError: If required_skills is invalid
        Exception: For database errors
    """
    try:
        # Validate input
        if not isinstance(required_skills, list):
            raise ValueError("Required skills must be a list")
        
        if not required_skills:
            return 1.0  # No requirements means perfect match
        
        # Get the resume
        from .get_resume import get_resume
        resume = await get_resume(session, resume_id)
        if not resume:
            return 0.0  # Return 0.0 for non-existent resumes instead of None
        
        # Use the resume's built-in skill matching method
        return resume.skill_match_score(required_skills)
        
    except ValueError:
        # Re-raise validation errors
        raise
    except Exception as e:
        print(f"Error in calculate_skill_match: {e}")
        import traceback
        traceback.print_exc()
        raise
