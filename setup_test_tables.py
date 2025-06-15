#!/usr/bin/env python3
"""
Create JIRA tables in test schema using the same connection approach as the tests.
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the workspace root to the Python path
workspace_root = Path(__file__).resolve().parent
sys.path.insert(0, str(workspace_root))

# Set environment variables like the tests do
os.environ["DATABASE_SCHEMA"] = "test"

# Import the FastAPI app to trigger the same database setup
from api.jira.main import app
from api.jira.lifespan import DATABASE_URL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text

async def create_test_tables():
    """Create test tables using the same database URL as the app."""
    print(f"Creating tables in test schema using: {DATABASE_URL}")
    
    # Read the SQL script
    sql_file = Path(__file__).parent / "create_jira_tables.sql"
    if not sql_file.exists():
        print(f"Error: SQL file not found at {sql_file}")
        return False
        
    with open(sql_file, 'r') as f:
        sql_commands = f.read()
    
    try:
        # Use the same database URL as the app
        engine = create_async_engine(DATABASE_URL, echo=True)
        
        async with engine.begin() as conn:
            print("Executing SQL commands...")
            # Execute the entire SQL script
            await conn.execute(text(sql_commands))
            print("✅ Tables created successfully!")
            
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(create_test_tables())
    sys.exit(0 if success else 1)
