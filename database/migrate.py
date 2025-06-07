#!/usr/bin/env python3
"""
Database migration runner for the Agentic Workforce Management API.
This script handles running SQL migration files in order.
"""

import sys
import asyncio
import logging
from run_migrations import run_migrations
from check_migration_status import check_migration_status

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        asyncio.run(check_migration_status())
    else:
        asyncio.run(run_migrations())


if __name__ == "__main__":
    main()
