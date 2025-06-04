from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.sql import select
from typing import List
from ..models import Board, EventCode, BoardEvent
from sqlalchemy.orm import Session
from .dependencies import get_session, get_webhook_manager, get_websocket_manager
from ..webhook_manager import WebhookManager
from ..websocket import WebsocketManager

router = APIRouter()

@router.post("/", response_model=Board)
async def create_board(
    board: Board,
    session: Session = Depends(get_session),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
    websocket_manager: WebsocketManager = Depends(get_websocket_manager),
):
    session.add(board)
    event = BoardEvent(event_code=EventCode.BOARD_CREATE, payload=board)
    await webhook_manager.broadcast(event=event)
    await websocket_manager.broadcast(event=event)
    await session.commit()
    await session.refresh(board)
    return board

@router.get("/", response_model=List[Board])
async def read_boards(session: Session = Depends(get_session)):
    result = await session.execute(select(Board))
    return result.scalars().all()

@router.get("/{board_id}", response_model=Board)
async def read_board(board_id: int, session: Session = Depends(get_session)):
    board = await session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@router.delete("/{board_id}", response_model=dict)
async def delete_board(
    board_id: int,
    session: Session = Depends(get_session),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
    websocket_manager: WebsocketManager = Depends(get_websocket_manager),
):
    board = await session.get(Board, board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    event = BoardEvent(event_code=EventCode.BOARD_DELETE, payload=board)
    await webhook_manager.broadcast(event=event)
    await websocket_manager.broadcast(event=event)
    await session.delete(board)
    await session.commit()
    return {"message": "Board deleted successfully"}