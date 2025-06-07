import os
import sys
import asyncpg  # type: ignore
import logging
from create_migration_table import create_migration_table
from get_executed_migrations import get_executed_migrations
from get_pending_migrations import get_pending_migrations
from execute_migration import execute_migration

logger = logging.getLogger(__name__)

# Database configuration from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jira:jira@docker.lan:5432/postgres")


async def run_migrations() -> None:
    """Run all pending migrations."""
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        logger.info("Connected to database")
        
        try:
            # Ensure migration table exists
            await create_migration_table(conn)
            
            # Get executed migrations
            executed_migrations = await get_executed_migrations(conn)
            logger.info(f"Found {len(executed_migrations)} executed migrations")
            
            # Get all migration files
            all_migrations = await get_pending_migrations()
            logger.info(f"Found {len(all_migrations)} total migration files")
            
            # Filter out already executed migrations
            pending_migrations = [
                (version, file_path) for version, file_path in all_migrations
                if version not in executed_migrations
            ]
            
            if not pending_migrations:
                logger.info("No pending migrations to execute")
                return
            
            logger.info(f"Found {len(pending_migrations)} pending migrations")
            
            # Execute pending migrations in order
            for version, file_path in pending_migrations:
                await execute_migration(conn, version, file_path)
            
            logger.info("All migrations completed successfully")
            
        finally:
            await conn.close()
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)
