from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...models import TicketComment, EventCode, TicketCommentEvent
from ..dependencies import get_session, get_webhook_manager, get_websocket_manager
from ...webhook_manager import WebhookManager
from ...websocket import WebsocketManager


async def update_comment(
    ticket_id: int,
    comment_id: int,
    comment: TicketComment,
    session: AsyncSession = Depends(get_session),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
    websocket_manager: WebsocketManager = Depends(get_websocket_manager),
):
    existing_comment = await session.get(TicketComment, comment_id)
    if not existing_comment or existing_comment.ticket_id != ticket_id:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    for key, value in comment.model_dump(exclude_unset=True).items():
        setattr(existing_comment, key, value)
    session.add(existing_comment)
    event = TicketCommentEvent(event_code=EventCode.COMMENT_EDIT, payload=comment)
    await webhook_manager.broadcast(event=event)
    await websocket_manager.broadcast(event=event)
    await session.commit()
    await session.refresh(existing_comment)
    return existing_comment
