"""
Add an experience entry to a resume.
Business logic function for experience management.
"""

import json
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from dateutil.parser import parse as parse_date

from ...models.resume import Resume


async def add_experience_to_resume(
    session: AsyncSession,
    resume_id: int,
    experience: Dict[str, Any]
) -> Optional[Resume]:
    """
    Add an experience entry to a resume.
    
    Args:
        session: Database session
        resume_id: Resume ID to update
        experience: Experience entry data
        
    Returns:
        Updated Resume object if successful, None if resume not found
        
    Raises:
        ValueError: If experience data is invalid
        Exception: For database errors
    """
    try:
        # Validate experience data
        if not experience or not isinstance(experience, dict):
            raise ValueError("Experience must be a dictionary")
        
        required_fields = ["company", "position", "start_date"]
        for field in required_fields:
            if field not in experience or not experience[field]:
                raise ValueError(f"Experience must include {field}")
        
        # Validate date format and future dates
        try:
            from datetime import datetime
            current_date = datetime.now().date()
            
            start_date = parse_date(experience["start_date"])
            if start_date.date() > current_date:
                raise ValueError("Start date cannot be in the future")
                
            if experience.get("end_date"):
                end_date = parse_date(experience["end_date"])
                if end_date.date() > current_date:
                    raise ValueError("End date cannot be in the future")
                if end_date < start_date:
                    raise ValueError("End date cannot be before start date")
        except (ValueError, TypeError) as e:
            if "cannot be in the future" in str(e) or "cannot be before" in str(e):
                raise
            raise ValueError(f"Invalid date format: {e}")
        
        # Set search path to test schema
        await session.execute(text("SET search_path TO test"))
        
        # Get current resume
        from .get_resume import get_resume
        resume = await get_resume(session, resume_id)
        if not resume:
            return None
        
        # Add experience using PostgreSQL JSONB array operations
        # Avoid ::jsonb casting on parameters to prevent SQLAlchemy mixed parameter issues
        await session.execute(
            text("""
            UPDATE resumes 
            SET experience = COALESCE(experience, '[]'::jsonb) || CAST(:experience_json AS jsonb),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :resume_id
            """),
            {"experience_json": json.dumps([experience]), "resume_id": resume_id}
        )
        
        await session.commit()
        
        # Return updated resume
        updated_resume = await get_resume(session, resume_id)
        return updated_resume
        
    except ValueError:
        # Re-raise validation errors without rollback
        raise
    except Exception as e:
        print(f"Error in add_experience_to_resume: {e}")
        import traceback
        traceback.print_exc()
        await session.rollback()
        raise
