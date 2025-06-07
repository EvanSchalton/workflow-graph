from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...models import TicketComment, EventCode, TicketCommentEvent
from ..dependencies import get_session, get_webhook_manager, get_websocket_manager
from ...webhook_manager import WebhookManager
from ...websocket import WebsocketManager


async def delete_comment(
    ticket_id: int,
    comment_id: int,
    session: AsyncSession = Depends(get_session),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
    websocket_manager: WebsocketManager = Depends(get_websocket_manager),
):
    comment = await session.get(TicketComment, comment_id)
    if not comment or comment.ticket_id != ticket_id:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    event = TicketCommentEvent(event_code=EventCode.COMMENT_DELETE, payload=comment)
    await webhook_manager.broadcast(event=event)
    await websocket_manager.broadcast(event=event)
    await session.delete(comment)
    await session.commit()
    return {"message": "Comment deleted successfully"}
