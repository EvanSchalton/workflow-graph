"""
Get all job descriptions with optional filtering and pagination.
Business logic function for retrieving multiple job descriptions.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.job_description import JobDescription


async def get_job_descriptions(
    session: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None
) -> List[JobDescription]:
    """
    Get all job descriptions with optional filtering and pagination.
    
    Args:
        session: Database session
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        filters: Optional filters to apply (e.g. department, experience_level)
        
    Returns:
        List of JobDescription objects
    """
    try:
        # Set search path to test schema
        await session.execute(text("SET search_path TO test"))
        
        # Start building the SQL query
        sql_query = """
        SELECT id, title, description, required_skills, experience_level, department, created_at, updated_at
        FROM job_descriptions
        WHERE 1=1
        """
        
        params = {}
        
        # Apply filters if provided
        if filters:
            if "department" in filters and filters["department"]:
                sql_query += " AND department = :department"
                params['department'] = filters["department"]
                
            if "experience_level" in filters and filters["experience_level"]:
                sql_query += " AND experience_level = :experience_level"
                params['experience_level'] = filters["experience_level"].value if hasattr(filters["experience_level"], 'value') else filters["experience_level"]
                
            if "skill" in filters and filters["skill"]:
                # For PostgreSQL JSONB arrays, use case-insensitive text search within JSON array
                sql_query += """ AND EXISTS (
                    SELECT 1 FROM jsonb_array_elements_text(required_skills) as skill
                    WHERE LOWER(skill) = LOWER(:skill)
                )"""
                params['skill'] = filters["skill"]
                
            if "title" in filters and filters["title"]:
                sql_query += " AND title ILIKE :title"
                params['title'] = f"%{filters['title']}%"
        
        # Apply pagination
        sql_query += " OFFSET :skip LIMIT :limit"
        params['skip'] = skip
        params['limit'] = limit
        
        # Execute query
        result = await session.execute(text(sql_query), params)
        
        # Convert results to JobDescription objects
        job_descriptions = []
        for row in result:
            try:
                job = JobDescription(
                    id=row.id, 
                    title=row.title,
                    description=row.description,
                    required_skills=row.required_skills,
                    experience_level=row.experience_level,
                    department=row.department,
                    created_at=row.created_at,
                    updated_at=row.updated_at
                )
                job_descriptions.append(job)
            except Exception as e:
                print(f"Error creating JobDescription from row: {e}")
                print(f"Row data: {row}")
        
        return job_descriptions
            
    except Exception as e:
        print(f"Error in get_job_descriptions: {e}")
        import traceback
        traceback.print_exc()
        return []
