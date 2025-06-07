"""
MCP (Model Context Protocol) routes for JIRA API.
This module provides MCP-compatible endpoints for JIRA resources and tools.
"""

from fastapi import APIRouter
from typing import List, Dict
from ...models.board import Board
from ...models.ticket import Ticket
from ...models.status_column import StatusColumn

# Import general JIRA route functions from their new locations
from ..boards.get_boards import get_boards
from ..boards.get_board_by_id import get_board_by_id
from ..boards.update_board import update_board
from ..boards.delete_board_with_events import delete_board_with_events
from ..tickets.get_tickets import get_tickets
from ..tickets.get_ticket_by_id import get_ticket_by_id
from ..tickets.update_ticket import update_ticket
from ..tickets.delete_ticket import delete_ticket
from ..columns.get_columns import get_columns
from ..columns.get_column_by_id import get_column_by_id
from ..columns.update_column import update_column
from ..columns.delete_column import delete_column

# Import MCP-specific functions
from .discover_resources import discover_resources
from .discover_tools import discover_tools

router = APIRouter()

# Board routes
router.get("/resources/boards", response_model=List[Board])(get_boards)
router.get("/resources/boards/{board_id}", response_model=Board)(get_board_by_id)
router.put("/resources/boards/{board_id}", response_model=Board)(update_board)
router.delete("/resources/boards/{board_id}", response_model=Dict[str, str])(delete_board_with_events)

# Ticket routes
router.get("/resources/tickets", response_model=List[Ticket])(get_tickets)
router.get("/resources/tickets/{ticket_id}", response_model=Ticket)(get_ticket_by_id)
router.put("/resources/tickets/{ticket_id}", response_model=Ticket)(update_ticket)
router.delete("/resources/tickets/{ticket_id}", response_model=Dict[str, str])(delete_ticket)

# Column routes
router.get("/resources/columns", response_model=List[StatusColumn])(get_columns)
router.get("/resources/columns/{column_id}", response_model=StatusColumn)(get_column_by_id)
router.put("/resources/columns/{column_id}", response_model=StatusColumn)(update_column)
router.delete("/resources/columns/{column_id}", response_model=Dict[str, str])(delete_column)

# Discovery routes
router.get("/resources", response_model=dict)(discover_resources)
router.get("/tools", response_model=dict)(discover_tools)

# Export the router for easy import
__all__ = ["router"]
