import asyncpg  # type: ignore
from typing import List


async def get_executed_migrations(conn: asyncpg.Connection) -> List[str]:
    """Get list of already executed migrations."""
    rows = await conn.fetch("SELECT version FROM schema_migrations ORDER BY version")
    return [row['version'] for row in rows]
