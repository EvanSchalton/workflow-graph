from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..dependencies import get_session
from ...models.board import Board


async def update_board(board_id: int, board: Board, session: AsyncSession = Depends(get_session)) -> Board:
    """Update a board."""
    existing_board = await session.get(Board, board_id)
    if not existing_board:
        raise HTTPException(status_code=404, detail="Board not found")
    for key, value in board.model_dump(exclude_unset=True).items():
        setattr(existing_board, key, value)
    session.add(existing_board)
    await session.commit()
    await session.refresh(existing_board)
    return existing_board
