"""
Find job descriptions that match the given skills and criteria.
Business logic function for finding matching job descriptions.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.job_description import JobDescription, ExperienceLevel


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
                    bonus_matches = 0.0
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
        def get_score(item: dict) -> float:
            score = item["match_score"]
            if isinstance(score, (int, float)):
                return float(score)
            return 0.0
        
        job_matches.sort(key=get_score, reverse=True)
        
        # Return limited results
        return job_matches[:limit]
            
    except Exception as e:
        print(f"Error in find_matching_job_descriptions: {e}")
        import traceback
        traceback.print_exc()
        return []
