#!/usr/bin/env python3
"""
Database migration runner for the Agentic Workforce Management API.
This script handles running SQL migration files in order.
"""

import os
import sys
import asyncio
import asyncpg  # type: ignore
from pathlib import Path
from typing import List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database configuration from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jira:jira@docker.lan:5432/postgres")
MIGRATIONS_DIR = Path(__file__).parent / "migrations"

async def create_migration_table(conn: asyncpg.Connection) -> None:
    """Create the migrations tracking table if it doesn't exist."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(255) PRIMARY KEY,
            executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    logger.info("Migration tracking table ensured")

async def get_executed_migrations(conn: asyncpg.Connection) -> List[str]:
    """Get list of already executed migrations."""
    rows = await conn.fetch("SELECT version FROM schema_migrations ORDER BY version")
    return [row['version'] for row in rows]

async def get_pending_migrations() -> List[Tuple[str, Path]]:
    """Get list of pending migration files."""
    if not MIGRATIONS_DIR.exists():
        logger.warning(f"Migrations directory {MIGRATIONS_DIR} does not exist")
        return []
    
    migration_files = []
    for file_path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        version = file_path.stem
        migration_files.append((version, file_path))
    
    return migration_files

async def execute_migration(conn: asyncpg.Connection, version: str, file_path: Path) -> None:
    """Execute a single migration file."""
    logger.info(f"Executing migration: {version}")
    
    # Read migration file
    with open(file_path, 'r') as f:
        migration_sql = f.read()
    
    # Execute within a transaction
    async with conn.transaction():
        try:
            await conn.execute(migration_sql)
            await conn.execute(
                "INSERT INTO schema_migrations (version) VALUES ($1)",
                version
            )
            logger.info(f"Migration {version} completed successfully")
        except Exception as e:
            logger.error(f"Migration {version} failed: {e}")
            raise

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

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        asyncio.run(check_migration_status())
    else:
        asyncio.run(run_migrations())

if __name__ == "__main__":
    main()
