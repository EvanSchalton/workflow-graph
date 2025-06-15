#!/usr/bin/env python3
"""
Script to create JIRA tables in the test schema for testing.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the workspace root to the Python path
workspace_root = Path(__file__).resolve().parent
sys.path.insert(0, str(workspace_root))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from sqlmodel import SQLModel

# Import all models to ensure they're registered with SQLModel
from api.jira.models.board import Board
from api.jira.models.status_column import StatusColumn  
from api.jira.models.ticket import Ticket
from api.jira.models.ticket_comment import TicketComment
from api.jira.models.webhook import Webhook

DATABASE_URL = "postgresql+asyncpg://jira:jira@docker.lan:5432/postgres"

async def create_test_schema():
    """Create test schema and JIRA tables."""
    print("Creating test schema and JIRA tables...")
    
    try:
        # Create engine
        print(f"Connecting to: {DATABASE_URL}")
        engine = create_async_engine(DATABASE_URL, echo=True)
        
        print("Testing connection...")
        async with engine.begin() as conn:
            version = await conn.execute(text("SELECT version()"))
            print(f"✅ Connected to PostgreSQL: {version.scalar()}")
            
            # Create test schema if it doesn't exist
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS test"))
            print("✅ Test schema created/verified")
            
            # Set search path to test schema
            await conn.execute(text("SET search_path TO test"))
            print("✅ Search path set to test schema")
            
            # Create all tables in test schema
            await conn.run_sync(SQLModel.metadata.create_all)
            print("✅ JIRA tables created in test schema")
            
        await engine.dispose()
        print("🎉 Test schema setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(create_test_schema())
