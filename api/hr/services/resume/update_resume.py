"""
Update an existing resume.
Business logic function for updating resumes.
"""

from datetime import datetime
from typing import Optional, Union, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.resume import Resume, ResumeUpdate


async def update_resume(
    session: AsyncSession,
    resume_id: int,
    resume_data: Union[ResumeUpdate, Dict[str, Any]]
) -> Optional[Resume]:
    """
    Update an existing resume.
    
    Args:
        session: Database session
        resume_id: ID of resume to update
        resume_data: Updated resume data
        
    Returns:
        Updated Resume object if successful, None if not found
        
    Raises:
        ValueError: If email is already in use by another resume
        Exception: For other database errors
    """
    try:
        # Set search path to test schema
        await session.execute(text("SET search_path TO test"))
        
        # Check if resume exists
        from .get_resume import get_resume
        existing_resume = await get_resume(session, resume_id)
        if not existing_resume:
            return None
        
        # Handle both dict and ResumeUpdate objects
        if isinstance(resume_data, dict):
            email = resume_data.get('email')
        else:
            email = resume_data.email
        
        # Check if email is being changed and if it's already in use
        if email and email.lower() != existing_resume.email.lower():
            email_check = await session.execute(
                text("SELECT id FROM resumes WHERE LOWER(email) = LOWER(:email) AND id != :resume_id"),
                {"email": email, "resume_id": resume_id}
            )
            if email_check.first():
                raise ValueError("'{email}' email already exists")
        
        # Build update query dynamically based on provided fields
        update_fields = []
        params = {"resume_id": resume_id, "updated_at": datetime.utcnow()}
        
        # Handle both dict and ResumeUpdate objects for field updates
        if isinstance(resume_data, dict):
            # Handle dict input
            for field_name, db_field in [
                ('name', 'name'),
                ('email', 'email'),
                ('phone', 'phone'),
                ('summary', 'summary'),
                ('skills', 'skills'),
                ('experience', 'experience'),
                ('education', 'education'),
                ('performance_history', 'performance_history')
            ]:
                if field_name in resume_data:
                    update_fields.append(f"{db_field} = :{db_field}")
                    params[db_field] = resume_data[field_name]
        else:
            # Handle ResumeUpdate object
            # Check each field and add to update if provided
            if resume_data.name is not None:
                update_fields.append("name = :name")
                params["name"] = resume_data.name
                
            if resume_data.email is not None:
                update_fields.append("email = :email")
                params["email"] = resume_data.email
                
            if resume_data.phone is not None:
                update_fields.append("phone = :phone")
                params["phone"] = resume_data.phone
                
            if resume_data.summary is not None:
                update_fields.append("summary = :summary")
                params["summary"] = resume_data.summary
                
            if resume_data.skills is not None:
                update_fields.append("skills = :skills")
                params["skills"] = resume_data.skills
                
            if resume_data.experience is not None:
                update_fields.append("experience = :experience")
                params["experience"] = resume_data.experience
                
            if resume_data.education is not None:
                update_fields.append("education = :education")
                params["education"] = resume_data.education
                
            if resume_data.performance_history is not None:
                update_fields.append("performance_history = :performance_history")
                params["performance_history"] = resume_data.performance_history
        
        # Always update the updated_at timestamp
        update_fields.append("updated_at = :updated_at")
        
        if len(update_fields) <= 1:  # Only updated_at field
            # Nothing meaningful to update
            return existing_resume
        
        # Execute update
        sql_query = f"""
        UPDATE resumes 
        SET {', '.join(update_fields)}
        WHERE id = :resume_id
        """
        
        await session.execute(text(sql_query), params)
        await session.commit()
        
        # Return updated resume
        updated_resume = await get_resume(session, resume_id)
        return updated_resume
        
    except ValueError:
        # Re-raise validation errors without rollback
        raise
    except Exception as e:
        print(f"Error in update_resume: {e}")
        import traceback
        traceback.print_exc()
        await session.rollback()
        raise
