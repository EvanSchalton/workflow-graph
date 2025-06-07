"""
Board management routes for JIRA API.
This module provides API endpoints for board CRUD operations with event notifications.
"""

from fastapi import APIRouter
from typing import List
from ...models import Board

# Import individual route functions
from .create_board import create_board
from .delete_board_with_events import delete_board_with_events

# Import read operations from local directory
from .get_boards import get_boards
from .get_board_by_id import get_board_by_id
from .update_board import update_board

router = APIRouter()

# Create route
router.post("/", response_model=Board)(create_board)

# Read routes
router.get("/", response_model=List[Board])(get_boards)
router.get("/{board_id}", response_model=Board)(get_board_by_id)

# Update route
router.put("/{board_id}", response_model=Board)(update_board)

# Delete route with events
router.delete("/{board_id}", response_model=dict)(delete_board_with_events)

# Export the router for easy import
__all__ = ["router"]
