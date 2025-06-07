from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...models import TicketComment, EventCode, TicketCommentEvent, Ticket
from ..dependencies import get_session, get_webhook_manager, get_websocket_manager
from ...webhook_manager import WebhookManager
from ...websocket import WebsocketManager


async def create_comment(
    ticket_id: int,
    comment: TicketComment,
    session: AsyncSession = Depends(get_session),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
    websocket_manager: WebsocketManager = Depends(get_websocket_manager),
):
    # Verify ticket exists
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    comment.ticket_id = ticket_id
    session.add(comment)
    event = TicketCommentEvent(event_code=EventCode.COMMENT_CREATE, payload=comment)
    await webhook_manager.broadcast(event=event)
    await websocket_manager.broadcast(event=event)
    await session.commit()
    await session.refresh(comment)
    return comment
