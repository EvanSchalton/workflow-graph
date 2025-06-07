from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..dependencies import get_session
from ...models.board import Board


async def get_board_by_id(board_id: int, session: AsyncSession = Depends(get_session)) -> Board:
    """Get a board by ID."""
    board = await session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board
