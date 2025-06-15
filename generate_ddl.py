#!/usr/bin/env python3
"""
Script to generate DDL for JIRA tables.
"""
import sys
from pathlib import Path

# Add the workspace root to the Python path
workspace_root = Path(__file__).resolve().parent
sys.path.insert(0, str(workspace_root))

from sqlalchemy import create_engine
from sqlmodel import SQLModel

# Import all models to ensure they're registered with SQLModel
from api.jira.models.board import Board
from api.jira.models.status_column import StatusColumn  
from api.jira.models.ticket import Ticket
from api.jira.models.ticket_comment import TicketComment
from api.jira.models.webhook import Webhook

def generate_ddl():
    """Generate DDL for JIRA tables."""
    print("-- DDL for JIRA tables in test schema")
    print("CREATE SCHEMA IF NOT EXISTS test;")
    print("SET search_path TO test;")
    print()
    
    # Create a mock engine just for DDL generation
    engine = create_engine("postgresql://user:pass@localhost/db", echo=False)
    
    # Generate DDL
    from sqlalchemy.schema import CreateTable
    
    for table in SQLModel.metadata.sorted_tables:
        print(f"-- Table: {table.name}")
        create_table_ddl = CreateTable(table).compile(engine)
        print(f"{create_table_ddl};")
        print()

if __name__ == "__main__":
    generate_ddl()
