from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from typing import List
from ..models.board import Board
from ..routes.get_session import get_session
from ..webhook_broadcaster import WebhookBroadcaster
from ..models.webhook import WebhookEventCode, BoardEvent

router = APIRouter()

@router.post("/", response_model=Board)
async def create_board(board: Board, session: AsyncSession = Depends(get_session)):
    session.add(board)
    await WebhookBroadcaster(session).broadcast(event=BoardEvent(event_code=WebhookEventCode.BOARD_CREATE, payload=board))
    await session.commit()
    await session.refresh(board)
    return board

@router.get("/", response_model=List[Board])
async def read_boards(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Board))
    return result.scalars().all()

@router.get("/{board_id}", response_model=Board)
async def read_board(board_id: int, session: AsyncSession = Depends(get_session)):
    board = await session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@router.delete("/{board_id}", response_model=dict)
async def delete_board(board_id: int, session: AsyncSession = Depends(get_session)):
    board = await session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    await WebhookBroadcaster(session).broadcast(event=BoardEvent(event_code=WebhookEventCode.BOARD_DELETE, payload=board))
    await session.delete(board)
    await session.commit()
    return {"message": "Board deleted successfully"}