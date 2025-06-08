from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...models import Board, EventCode, BoardEvent
from ..dependencies import get_session, get_webhook_manager, get_websocket_manager
from ...webhook_manager import WebhookManager
from ...websocket import WebsocketManager
from pydantic import ValidationError


async def create_board(
    board: Board,
    session: AsyncSession = Depends(get_session),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
    websocket_manager: WebsocketManager = Depends(get_websocket_manager),
) -> Board:
    """Create a new board with webhook and websocket notifications."""
    # Validate required fields
    if not board.name or not board.name.strip():
        raise HTTPException(status_code=422, detail="Board name is required")
        
    session.add(board)
    event = BoardEvent(event_code=EventCode.BOARD_CREATE, payload=board)
    await webhook_manager.broadcast(event=event)
    await websocket_manager.broadcast(event=event)
    await session.commit()
    await session.refresh(board)
    return board
