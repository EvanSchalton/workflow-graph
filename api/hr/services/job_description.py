"""
JobDescription service for CRUD operations.
This service implements business logic for managing job descriptions.
"""

from typing import List, Optional, Dict, Any, Union, TypeVar, cast
from sqlalchemy import select, update, delete, or_, and_, Column, String, Text, Boolean, text
from sqlalchemy.sql import expression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement
from fastapi import HTTPException, status
from datetime import datetime

# Type variable for comparison operators
T = TypeVar("T")

from ..models.job_description import (
    JobDescription,
    JobDescriptionCreate,
    JobDescriptionUpdate,
    JobDescriptionRead,
    ExperienceLevel
)


async def get_job_description(
    session: AsyncSession,
    job_id: int
) -> Optional[JobDescription]:
    """
    Get a job description by ID.
    
    Args:
        session: Database session
        job_id: ID of the job description to retrieve
        
    Returns:
        JobDescription object if found, None otherwise
    """
    try:
        # Set search path to test schema first
        await session.execute(text("SET search_path TO test"))
        
        # Create a fresh query to work with the test schema
        raw_sql = f"""
        SELECT id, title, description, required_skills, experience_level, department, created_at, updated_at
        FROM job_descriptions
        WHERE id = {job_id}
        """
        result = await session.execute(text(raw_sql))
        
        # Map result to JobDescription model
        for row in result:
            # If we have any result, convert the first one to a JobDescription and return it
            # Debug info
            print(f"Found job with ID {job_id}: {row}")
            try:
                # Format experience_level properly
                exp_level = row.experience_level
                if isinstance(exp_level, str):
                    exp_level = ExperienceLevel(exp_level.lower())
                
                return JobDescription(
                    id=row.id, 
                    title=row.title,
                    description=row.description,
                    required_skills=row.required_skills,
                    experience_level=exp_level,
                    department=row.department,
                    created_at=row.created_at,
                    updated_at=row.updated_at
                )
            except Exception as e:
                print(f"Error creating JobDescription from row: {e}")
                print(f"Row data: {row}")
                raise
        
        # No result found
        print(f"No job found with ID {job_id}")
        return None
            
    except Exception as e:
        # Print any exceptions for debugging
        print(f"Error in get_job_description: {e}")
        import traceback
        traceback.print_exc()
        return None


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


async def create_job_description(
    session: AsyncSession,
    job_data: JobDescriptionCreate
) -> JobDescription:
    """
    Create a new job description.
    
    Args:
        session: Database session
        job_data: New job description data
        
    Returns:
        Created JobDescription object
    """
    try:
        # Set search path to test schema
        await session.execute(text("SET search_path TO test"))
        
        # Normalize experience level - make sure it's an enum instance
        experience_level = job_data.experience_level
        if isinstance(experience_level, str):
            experience_level = ExperienceLevel(experience_level.lower())
            
        # Create job description instance
        job = JobDescription(
            title=job_data.title,
            description=job_data.description,
            required_skills=job_data.required_skills,
            experience_level=experience_level,
            department=job_data.department,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add to session and commit
        session.add(job)
        await session.commit()
        
        # Get the job by ID using our get_job_description function
        # which is already handling JSONB data type correctly
        if job.id:
            # Return a freshly loaded instance that is properly initialized
            job = await get_job_description(session, job.id)
            
            # Make sure experience_level is an ExperienceLevel enum, not a string
            if job and isinstance(job.experience_level, str):
                job.experience_level = ExperienceLevel(job.experience_level.lower())
            
            return job
        
        return job
    except Exception as e:
        print(f"Error in create_job_description: {e}")
        import traceback
        traceback.print_exc()
        await session.rollback()
        raise


async def update_job_description(
    session: AsyncSession,
    job_id: int,
    job_data: JobDescriptionUpdate
) -> Optional[JobDescription]:
    """
    Update an existing job description.
    
    Args:
        session: Database session
        job_id: ID of the job description to update
        job_data: Updated job description data
        
    Returns:
        Updated JobDescription object if found, None otherwise
    """
    try:
        # Set search path to test schema
        await session.execute(text("SET search_path TO test"))
        
        # Get the existing job description
        job = await get_job_description(session, job_id)
        if not job:
            return None
        
        # Prepare update data, excluding None values
        update_data = job_data.model_dump(exclude_unset=True)
        if not update_data:
            # No valid update data provided
            return job
        
        # Fix experience_level if it's in the update data
        if 'experience_level' in update_data:
            if isinstance(update_data['experience_level'], str):
                # Convert string to enum if needed
                update_data['experience_level'] = ExperienceLevel(update_data['experience_level'].lower())
            elif hasattr(update_data['experience_level'], 'value'):
                # Use the enum value
                update_data['experience_level'] = update_data['experience_level'].value
        
        # Always update the updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        # Build SQL update statement for JSONB compatibility
        set_clauses = []
        params = {'job_id': job_id}
        
        for key, value in update_data.items():
            if key == 'required_skills':
                # Handle JSONB type
                set_clauses.append(f"required_skills = CAST(:required_skills AS jsonb)")
                params['required_skills'] = value
            else:
                set_clauses.append(f"{key} = :{key}")
                params[key] = value
        
        sql = f"""
        UPDATE job_descriptions 
        SET {', '.join(set_clauses)}
        WHERE id = :job_id
        """
        
        # Execute the update
        await session.execute(text(sql), params)
        await session.commit()
        
        # Get the updated job description
        return await get_job_description(session, job_id)
    except Exception as e:
        print(f"Error in update_job_description: {e}")
        import traceback
        traceback.print_exc()
        await session.rollback()
        return None


async def delete_job_description(
    session: AsyncSession,
    job_id: int
) -> bool:
    """
    Delete a job description by ID.
    
    Args:
        session: Database session
        job_id: ID of the job description to delete
        
    Returns:
        True if deleted, False if not found
    """
    try:
        # Set search path to test schema
        await session.execute(text("SET search_path TO test"))
        
        # Check if job exists
        job = await get_job_description(session, job_id)
        if not job:
            return False
        
        # In a test environment, we might not need this check
        # In real environment, you should check for relations before deleting
        # For simplicity, we're using raw SQL for the delete operation
        sql = "DELETE FROM job_descriptions WHERE id = :job_id"
        params = {'job_id': job_id}
        
        # Execute the delete
        await session.execute(text(sql), params)
        await session.commit()
        
        return True
    except Exception as e:
        print(f"Error in delete_job_description: {e}")
        import traceback
        traceback.print_exc()
        await session.rollback()
        return False


async def add_skill_to_job_description(
    session: AsyncSession,
    job_id: int,
    skill: str
) -> Optional[JobDescription]:
    """
    Add a required skill to a job description.
    
    Args:
        session: Database session
        job_id: ID of the job description
        skill: Skill to add
        
    Returns:
        Updated JobDescription object if found, None otherwise
    """
    try:
        # Set search path to test schema
        await session.execute(text("SET search_path TO test"))
        
        # Get the existing job description
        job = await get_job_description(session, job_id)
        if not job:
            return None
        
        # Check if the skill already exists in required_skills (case insensitive)
        skill_exists = False
        for existing_skill in job.required_skills:
            if existing_skill.lower() == skill.lower():
                skill_exists = True
                break
        
        # Only add the skill if it's not already present
        if not skill_exists:
            # For JSONB arrays, we need to use PostgreSQL's jsonb_array_append function
            sql = """
            UPDATE job_descriptions
            SET 
                required_skills = CASE 
                    WHEN required_skills IS NULL THEN CAST(:new_array AS jsonb)
                    ELSE required_skills || CAST(:new_skill AS jsonb)
                END,
                updated_at = :updated_at
            WHERE id = :job_id
            """
            
            params = {
                'job_id': job_id,
                'new_skill': f'"{skill.strip()}"',
                'new_array': f'["{skill.strip()}"]',
                'updated_at': datetime.utcnow()
            }
            
            # Execute the update
            await session.execute(text(sql), params)
            await session.commit()
        
        # Get the updated job description
        return await get_job_description(session, job_id)
        
    except Exception as e:
        print(f"Error in add_skill_to_job_description: {e}")
        import traceback
        traceback.print_exc()
        await session.rollback()
        return None


async def remove_skill_from_job_description(
    session: AsyncSession,
    job_id: int,
    skill: str
) -> Optional[JobDescription]:
    """
    Remove a required skill from a job description.
    
    Args:
        session: Database session
        job_id: ID of the job description
        skill: Skill to remove
        
    Returns:
        Updated JobDescription object if found, None otherwise
    """
    try:
        # Set search path to test schema
        await session.execute(text("SET search_path TO test"))
        
        # Get the existing job description
        job = await get_job_description(session, job_id)
        if not job:
            return None
            
        # Find the skill index in the array (case insensitive)
        remove_index = None
        new_skills = []
        
        for i, existing_skill in enumerate(job.required_skills):
            if existing_skill.lower() == skill.lower():
                remove_index = i
            else:
                new_skills.append(existing_skill)
        
        # Only update if the skill was found
        if remove_index is not None:
            # For JSONB, we need to create a new array without the removed skill
            import json
            sql = """
            UPDATE job_descriptions
            SET 
                required_skills = CAST(:new_skills AS jsonb),
                updated_at = :updated_at
            WHERE id = :job_id
            """
            
            params = {
                'job_id': job_id,
                'new_skills': json.dumps(new_skills),  # Convert list to JSON string
                'updated_at': datetime.utcnow()
            }
            
            # Execute the update
            await session.execute(text(sql), params)
            await session.commit()
        
        # Get the updated job description
        return await get_job_description(session, job_id)
            
    except Exception as e:
        print(f"Error in remove_skill_from_job_description: {e}")
        import traceback
        traceback.print_exc()
        await session.rollback()
        return None


async def find_matching_job_descriptions(
    session: AsyncSession,
    skills: List[str],
    experience_level: Optional[ExperienceLevel] = None,
    department: Optional[str] = None,
    match_threshold: float = 0.1,  # Lower threshold to allow partial matches
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Find job descriptions that match the given skills and criteria.
    
    Args:
        session: Database session
        skills: List of skills to match against
        experience_level: Optional experience level to filter by
        department: Optional department to filter by
        match_threshold: Minimum match score threshold (0.0 to 1.0)
        limit: Maximum number of results to return
        
    Returns:
        List of job descriptions with match scores, sorted by score descending
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
        if experience_level:
            sql_query += " AND experience_level = :experience_level"
            if hasattr(experience_level, 'value'):
                # If it's an enum instance, use its value
                params['experience_level'] = experience_level.value
            else:
                # Otherwise assume it's a string
                params['experience_level'] = str(experience_level)
            
        if department:
            sql_query += " AND department = :department"
            params['department'] = department
        
        # Execute query
        result = await session.execute(text(sql_query), params)
         # Convert results to JobDescription objects and calculate match scores
        job_matches = []
        
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
                
                # Calculate match score using the job's matches_skills method
                match_score = job.matches_skills(skills)
                
                # Add bonus score for additional related skills
                if job.required_skills and skills:
                    # Convert to lowercase for case-insensitive comparison
                    required_lower = [skill.lower() for skill in job.required_skills]
                    candidate_lower = [skill.lower() for skill in skills]
                    
                    # Add bonus for additional relevant skills
                    bonus_matches = 0
                    for cand_skill in candidate_lower:
                        if not any(cand_skill == req.lower() for req in job.required_skills):
                            for req_skill in required_lower:
                                # This is a skill not explicitly required but related
                                if cand_skill in req_skill or req_skill in cand_skill:
                                    bonus_matches += 0.1
                                    break
                    
                    # Add the bonus to the match score (up to 1.0 maximum)
                    match_score = min(1.0, match_score + bonus_matches)
                
                if match_score >= match_threshold:
                    job_matches.append({
                        "job": job,
                        "match_score": match_score
                    })
            except Exception as e:
                print(f"Error processing job for matching: {e}")
                print(f"Row data: {row}")
        
        # Sort by match score descending
        job_matches.sort(key=lambda item: float(item["match_score"]), reverse=True)
        
        # Return limited results
        return job_matches[:limit]
            
    except Exception as e:
        print(f"Error in find_matching_job_descriptions: {e}")
        import traceback
        traceback.print_exc()
        return []
