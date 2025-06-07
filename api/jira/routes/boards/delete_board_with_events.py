from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...models import Board, EventCode, BoardEvent
from ..dependencies import get_session, get_webhook_manager, get_websocket_manager
from ...webhook_manager import WebhookManager
from ...websocket import WebsocketManager


async def delete_board_with_events(
    board_id: int,
    session: AsyncSession = Depends(get_session),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
    websocket_manager: WebsocketManager = Depends(get_websocket_manager),
) -> dict:
    """Delete a board with webhook and websocket notifications."""
    board = await session.get(Board, board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    
    event = BoardEvent(event_code=EventCode.BOARD_DELETE, payload=board)
    await webhook_manager.broadcast(event=event)
    await websocket_manager.broadcast(event=event)
    await session.delete(board)
    await session.commit()
    return {"message": "Board deleted successfully"}
