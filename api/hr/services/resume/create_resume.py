"""
Create a new resume.
Business logic function for creating resumes.
"""

import re
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, Dict, Any

from ...models.resume import Resume, ResumeCreate


async def create_resume(
    session: AsyncSession,
    resume_data: Union[ResumeCreate, Dict[str, Any]]
) -> Resume:
    """
    Create a new resume.
    
    Args:
        session: Database session
        resume_data: New resume data
        
    Returns:
        Created Resume object
        
    Raises:
        ValueError: If email is already in use or validation fails
        Exception: For other database errors
    """
    try:
        # Set search path to test schema
        await session.execute(text("SET search_path TO test"))
        
        # Validate input - handle both dict and ResumeCreate objects
        if isinstance(resume_data, dict):
            # Validate required fields for dict input
            if not resume_data.get('email'):
                raise ValueError("Email is required")
            if not resume_data.get('name'):
                raise ValueError("Name is required")
        else:
            # It should be a ResumeCreate object
            if not resume_data.email:
                raise ValueError("Email is required")
            if not resume_data.name:
                raise ValueError("Name is required")
        
        # Get email for validation
        email = resume_data.get('email') if isinstance(resume_data, dict) else resume_data.email
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        
        # Validate experience dates (only if experience is provided)
        experience = resume_data.get('experience', []) if isinstance(resume_data, dict) else (resume_data.experience or [])
        for exp in experience:
            start_date = exp.get('start_date') if isinstance(exp, dict) else exp.start_date
            end_date = exp.get('end_date') if isinstance(exp, dict) else exp.end_date
            
            if start_date:
                try:
                    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                    if start_datetime > datetime.now():
                        raise ValueError("Future dates not allowed in experience")
                except ValueError as e:
                    if "Future dates not allowed" in str(e):
                        raise
                    # Continue if date parsing fails - let the database handle it
            
            if end_date:
                try:
                    end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                    if end_datetime > datetime.now():
                        raise ValueError("Future dates not allowed in experience")
                except ValueError as e:
                    if "Future dates not allowed" in str(e):
                        raise
                    # Continue if date parsing fails - let the database handle it
        
        # Check if email already exists
        existing_check = await session.execute(
            text("SELECT id FROM resumes WHERE LOWER(email) = LOWER(:email)"),
            {"email": email}
        )
        if existing_check.first():
            raise ValueError(f"'{email}' email already exists")
        
        # Convert dict to ResumeCreate if needed
        if isinstance(resume_data, dict):
            resume_data = ResumeCreate(
                name=resume_data.get('name', ''),
                email=resume_data.get('email', ''),
                phone=resume_data.get('phone'),
                summary=resume_data.get('summary'),
                skills=resume_data.get('skills', []),
                experience=resume_data.get('experience', []),
                education=resume_data.get('education', []),
                performance_history=resume_data.get('performance_history', {})
            )
        
        # Create resume instance
        resume = Resume(
            name=resume_data.name,
            email=resume_data.email,
            phone=resume_data.phone,
            summary=resume_data.summary,
            skills=resume_data.skills,
            experience=resume_data.experience,
            education=resume_data.education,
            performance_history=resume_data.performance_history,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add to session and commit
        session.add(resume)
        await session.commit()
        
        # Import here to avoid circular imports
        from .get_resume import get_resume
        
        # Return a freshly loaded instance
        if resume.id:
            refreshed_resume = await get_resume(session, resume.id)
            if refreshed_resume:
                return refreshed_resume
        
        return resume
        
    except ValueError:
        # Re-raise validation errors without rollback
        raise
    except Exception as e:
        print(f"Error in create_resume: {e}")
        import traceback
        traceback.print_exc()
        await session.rollback()
        raise
