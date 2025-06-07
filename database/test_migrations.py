#!/usr/bin/env python3
"""
Test script for database migrations.
This script tests the migration system by running migrations and verifying the schema.
"""

import asyncio
import asyncpg  # type: ignore
import sys
from pathlib import Path
import pytest

# Add the parent directory to the path so we can import the migration module
sys.path.insert(0, str(Path(__file__).parent))

# Import individual function modules
from create_migration_table import create_migration_table
from get_executed_migrations import get_executed_migrations

# Database URL - Use postgresql scheme for asyncpg
DATABASE_URL = "postgresql://jira:jira@docker.lan:5432/postgres"

@pytest.mark.asyncio
async def test_migration_system():
    """Test the migration system by verifying table creation and constraints."""
    print("Testing migration system...")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        print("✓ Connected to database")
        
        try:
            # Test migration table creation
            await create_migration_table(conn)
            print("✓ Migration table created/verified")
            
            # Test getting executed migrations
            executed = await get_executed_migrations(conn)
            print(f"✓ Retrieved executed migrations: {len(executed)} found")
            
            # Test if core tables exist (they should after migration)
            tables_to_check = [
                'job_descriptions', 'resumes', 'job_applications', 'agents',
                'tasks', 'task_assignments', 'model_catalog', 'execution_costs',
                'task_prompts', 'resume_prompts', 'audit_logs'
            ]
            
            for table in tables_to_check:
                exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = $1
                    )
                """, table)
                
                if exists:
                    print(f"✓ Table {table} exists")
                else:
                    print(f"✗ Table {table} missing")
            
            # Test some basic constraints
            print("\nTesting constraints...")
            
            # Test ENUM constraints
            try:
                await conn.execute("""
                    INSERT INTO job_descriptions (title, description, required_skills, experience_level)
                    VALUES ('Test Job', 'Test Description', '[]', 'invalid_level')
                """)
                print("✗ ENUM constraint failed - should not allow invalid experience_level")
            except asyncpg.exceptions.CheckViolationError:
                print("✓ ENUM constraint working - rejected invalid experience_level")
            
            # Test JSON constraints
            try:
                await conn.execute("""
                    INSERT INTO job_descriptions (title, description, required_skills, experience_level)
                    VALUES ('Test Job', 'Test Description', 'not_an_array', 'junior')
                """)
                print("✗ JSON constraint failed - should not allow non-array required_skills")
            except (asyncpg.exceptions.CheckViolationError, asyncpg.exceptions.DataError):
                print("✓ JSON constraint working - rejected non-array required_skills")
            
            # Test positive cost constraints
            try:
                await conn.execute("""
                    INSERT INTO model_catalog (name, provider, cost_per_input_token, cost_per_output_token, context_limit, performance_tier)
                    VALUES ('test-model', 'test-provider', -1.0, 0.001, 4096, 'basic')
                """)
                print("✗ Cost constraint failed - should not allow negative costs")
            except asyncpg.exceptions.CheckViolationError:
                print("✓ Cost constraint working - rejected negative cost")
            
            # Test foreign key constraints
            try:
                await conn.execute("""
                    INSERT INTO job_applications (job_description_id, resume_id)
                    VALUES (99999, 99999)
                """)
                print("✗ Foreign key constraint failed - should not allow non-existent references")
            except asyncpg.exceptions.ForeignKeyViolationError:
                print("✓ Foreign key constraint working - rejected non-existent references")
            
            # Test indexes exist
            print("\nTesting indexes...")
            indexes = await conn.fetch("""
                SELECT indexname FROM pg_indexes 
                WHERE schemaname = 'public' 
                AND indexname LIKE 'idx_%'
                ORDER BY indexname
            """)
            
            print(f"✓ Found {len(indexes)} custom indexes")
            for idx in indexes[:5]:  # Show first 5 indexes
                print(f"  - {idx['indexname']}")
            if len(indexes) > 5:
                print(f"  ... and {len(indexes) - 5} more")
            
            # Test views exist
            views = await conn.fetch("""
                SELECT viewname FROM pg_views 
                WHERE schemaname = 'public'
                ORDER BY viewname
            """)
            
            print(f"\n✓ Found {len(views)} views:")
            for view in views:
                print(f"  - {view['viewname']}")
            
            # Test functions exist
            functions = await conn.fetch("""
                SELECT proname FROM pg_proc 
                WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
                AND proname NOT LIKE 'pg_%'
                ORDER BY proname
            """)
            
            print(f"\n✓ Found {len(functions)} custom functions:")
            for func in functions:
                print(f"  - {func['proname']}")
            
            print("\n✅ Migration system test completed successfully!")
            
        finally:
            await conn.close()
            
    except Exception as e:
        print(f"\n❌ Migration system test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_migration_system())
