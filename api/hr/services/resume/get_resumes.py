"""
Get all resumes with optional filtering and pagination.
Business logic function for retrieving multiple resumes.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.resume import Resume


async def get_resumes(
    session: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None
) -> List[Resume]:
    """
    Get all resumes with optional filtering and pagination.
    
    Args:
        session: Database session
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        filters: Optional filters to apply (e.g. skill, name, email)
        
    Returns:
        List of Resume objects
    """
    try:
        # Set search path to test schema
        await session.execute(text("SET search_path TO test"))
        
        # Start building the SQL query
        sql_query = """
        SELECT id, name, email, phone, summary, skills, experience, 
               education, performance_history, created_at, updated_at
        FROM resumes
        WHERE 1=1
        """
        
        params = {}
        
        # Apply filters if provided
        if filters:
            if "name" in filters and filters["name"]:
                sql_query += " AND name ILIKE :name"
                params['name'] = f"%{filters['name']}%"
                
            if "email" in filters and filters["email"]:
                sql_query += " AND email ILIKE :email"
                params['email'] = f"%{filters['email']}%"
                
            if "skill" in filters and filters["skill"]:
                # For PostgreSQL array, use ANY operator with case-insensitive comparison
                sql_query += " AND EXISTS (SELECT 1 FROM unnest(skills) AS skill WHERE LOWER(skill) = LOWER(:skill))"
                params['skill'] = filters["skill"]
                
            if "min_experience_years" in filters and filters["min_experience_years"] is not None:
                # This is a complex filter that would require calculating experience years
                # For now, we'll skip this and handle it in post-processing
                pass
                
            if "has_education" in filters and filters["has_education"] is not None:
                if filters["has_education"]:
                    sql_query += " AND jsonb_array_length(education) > 0"
                else:
                    sql_query += " AND (education IS NULL OR jsonb_array_length(education) = 0)"
        
        # Apply pagination
        sql_query += " ORDER BY created_at DESC OFFSET :skip LIMIT :limit"
        params['skip'] = skip
        params['limit'] = limit
        
        # Execute query
        result = await session.execute(text(sql_query), params)
        
        # Convert results to Resume objects
        resumes = []
        for row in result:
            try:
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
                
                # Post-process for complex filters
                if filters and "min_experience_years" in filters and filters["min_experience_years"] is not None:
                    if resume.calculate_experience_years() < filters["min_experience_years"]:
                        continue
                
                resumes.append(resume)
            except Exception as e:
                print(f"Error creating Resume from row: {e}")
                print(f"Row data: {row}")
        
        return resumes
            
    except Exception as e:
        print(f"Error in get_resumes: {e}")
        import traceback
        traceback.print_exc()
        return []
