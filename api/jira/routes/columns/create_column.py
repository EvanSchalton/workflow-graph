from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ...models import StatusColumn, EventCode, StatusColumnEvent
from ..dependencies import get_session, get_webhook_manager, get_websocket_manager
from ...webhook_manager import WebhookManager
from ...websocket import WebsocketManager


async def create_column(
    column: StatusColumn,
    session: AsyncSession = Depends(get_session),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
    websocket_manager: WebsocketManager = Depends(get_websocket_manager),
):
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
