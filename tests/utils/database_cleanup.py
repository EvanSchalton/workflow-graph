"""Database cleanup utilities for test isolation."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel


async def cleanup_test_schema(session: AsyncSession, schema_name: str = "test") -> None:
    """
    Clean up all data in the test schema while preserving the schema structure.
    
    This function truncates all tables in the specified schema to ensure
    clean state between tests while avoiding the overhead of dropping/recreating
    the entire schema.
    
    Args:
        session: The database session to use for cleanup
        schema_name: The name of the schema to clean up
    """
    try:
        # Get all table names in the schema
        tables_query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = :schema_name 
            AND table_type = 'BASE TABLE'
        """)
        
        result = await session.execute(tables_query, {"schema_name": schema_name})
        tables = [row[0] for row in result.fetchall()]
        
        if not tables:
            return
        
        # Disable foreign key checks temporarily to avoid constraint issues
        await session.execute(text("SET session_replication_role = replica;"))
        
        # Truncate all tables in the schema
        for table in tables:
            await session.execute(text(f"TRUNCATE TABLE {schema_name}.{table} RESTART IDENTITY CASCADE;"))
        
        # Re-enable foreign key checks
        await session.execute(text("SET session_replication_role = DEFAULT;"))
        
        # Commit the cleanup
        await session.commit()
        
    except Exception as e:
        # Rollback in case of any error
        await session.rollback()
        # Re-enable foreign key checks in case they were disabled
        try:
            await session.execute(text("SET session_replication_role = DEFAULT;"))
            await session.commit()
        except:
            pass
        raise e


async def reset_test_schema(session: AsyncSession, schema_name: str = "test") -> None:
    """
    Reset the test schema by dropping and recreating it.
    
    This is a more thorough cleanup that removes all data and recreates
    the schema structure. Use this when you need a completely fresh start.
    
    Args:
        session: The database session to use for reset
        schema_name: The name of the schema to reset
    """
    try:
        # Drop the schema and all its contents
        await session.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;"))
        
        # Recreate the schema
        await session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name};"))
        
        # Set the search path to the schema
        await session.execute(text(f"SET search_path TO {schema_name};"))
        
        # Recreate all tables using SQLModel metadata
        await session.run_sync(SQLModel.metadata.create_all)
        
        # Commit the changes
        await session.commit()
        
    except Exception as e:
        await session.rollback()
        raise e


async def ensure_clean_test_environment(session: AsyncSession, schema_name: str = "test") -> None:
    """
    Ensure a clean test environment by cleaning up existing data.
    
    This function provides a fast cleanup suitable for running between tests
    to ensure test isolation without the overhead of schema recreation.
    
    Args:
        session: The database session to use
        schema_name: The name of the schema to clean
    """
    await cleanup_test_schema(session, schema_name)
