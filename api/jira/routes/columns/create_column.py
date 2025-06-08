from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from ...models import StatusColumn, EventCode, StatusColumnEvent, Board
from ..dependencies import get_session, get_webhook_manager, get_websocket_manager
from ...webhook_manager import WebhookManager
from ...websocket import WebsocketManager


async def create_column(
    column: StatusColumn,
    session: AsyncSession = Depends(get_session),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
    websocket_manager: WebsocketManager = Depends(get_websocket_manager),
):
    # Validate required fields
    if not column.name or not column.name.strip():
        raise HTTPException(status_code=422, detail="Column name is required")
    
    # Check if the board_id exists
    if column.board_id:
        result = await session.execute(select(Board).where(Board.id == column.board_id))
        board = result.scalar_one_or_none()
        if not board:
            raise HTTPException(status_code=404, detail=f"Board with ID {column.board_id} not found")
    else:
        raise HTTPException(status_code=422, detail="board_id is required")
    
    session.add(column)
    event = StatusColumnEvent(
        event_code=EventCode.COLUMN_CREATE,
        payload=column
    )
    await webhook_manager.broadcast(event=event)
    await websocket_manager.broadcast(event=event)
    await session.commit()
    await session.refresh(column)
    return column
