from pathlib import Path
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

# Migrations directory relative to this file's parent
MIGRATIONS_DIR = Path(__file__).parent / "migrations"


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
