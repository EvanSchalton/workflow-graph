import os
import sys
import asyncpg  # type: ignore
import logging
from create_migration_table import create_migration_table
from get_executed_migrations import get_executed_migrations
from get_pending_migrations import get_pending_migrations

logger = logging.getLogger(__name__)

# Database configuration from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jira:jira@docker.lan:5432/postgres")


async def check_migration_status() -> None:
    """Check the status of migrations without executing them."""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        logger.info("Connected to database")
        
        try:
            # Ensure migration table exists
            await create_migration_table(conn)
            
            # Get executed migrations
            executed_migrations = await get_executed_migrations(conn)
            
            # Get all migration files
            all_migrations = await get_pending_migrations()
            
            print("\nMigration Status:")
            print("=" * 50)
            
            for version, file_path in all_migrations:
                status = "EXECUTED" if version in executed_migrations else "PENDING"
                print(f"{version:<30} {status}")
            
            pending_count = len([v for v, _ in all_migrations if v not in executed_migrations])
            print(f"\nSummary: {len(executed_migrations)} executed, {pending_count} pending")
            
        finally:
            await conn.close()
            
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        sys.exit(1)
