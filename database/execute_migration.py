import asyncpg  # type: ignore
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


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
