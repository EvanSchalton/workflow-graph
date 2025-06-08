"""
Update the entire experience array for a resume.
Business logic function for experience management.
"""

import json
from typing import Optional, List, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from dateutil.parser import parse as parse_date

from ...models.resume import Resume


async def update_resume_experience(
    session: AsyncSession,
    resume_id: int,
    experience_list: List[Dict[str, Any]]
) -> Optional[Resume]:
    """
    Update the entire experience array for a resume.
    
    Args:
        session: Database session
        resume_id: Resume ID to update
        experience_list: List of experience entries
        
    Returns:
        Updated Resume object if successful, None if resume not found
        
    Raises:
        ValueError: If experience data is invalid
        Exception: For database errors
    """
    try:
        # Validate experience data
        if not isinstance(experience_list, list):
            raise ValueError("Experience must be a list")
        
        # Validate each experience entry
        for i, experience in enumerate(experience_list):
            if not isinstance(experience, dict):
                raise ValueError(f"Experience entry {i} must be a dictionary")
            
            required_fields = ["company", "position", "start_date"]
            for field in required_fields:
                if field not in experience or not experience[field]:
                    raise ValueError(f"Experience entry {i} must include {field}")
            
            # Validate date format
            try:
                start_date = parse_date(experience["start_date"])
                if experience.get("end_date"):
                    end_date = parse_date(experience["end_date"])
                    if end_date < start_date:
                        raise ValueError(f"Experience entry {i}: End date cannot be before start date")
            except (ValueError, TypeError) as e:
                raise ValueError(f"Experience entry {i}: Invalid date format: {e}")
        
        # Set search path to test schema
        await session.execute(text("SET search_path TO test"))
        
        # Get current resume
        from .get_resume import get_resume
        resume = await get_resume(session, resume_id)
        if not resume:
            return None
        
        # Update experience using PostgreSQL JSONB
        query = text("""
            UPDATE resumes 
            SET experience = CAST(:experience_json AS jsonb),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :resume_id
            """)
        
        await session.execute(query, {"experience_json": json.dumps(experience_list), "resume_id": resume_id})
        
        await session.commit()
        
        # Return updated resume
        updated_resume = await get_resume(session, resume_id)
        return updated_resume
        
    except ValueError:
        # Re-raise validation errors without rollback
        raise
    except Exception as e:
        print(f"Error in update_resume_experience: {e}")
        import traceback
        traceback.print_exc()
        await session.rollback()
        raise
