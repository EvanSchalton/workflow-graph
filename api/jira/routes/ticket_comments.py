from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.sql import select, text
from typing import List
from ..models import TicketComment, EventCode, TicketCommentEvent, Ticket
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import get_session, get_webhook_manager, get_websocket_manager
from ..webhook_manager import WebhookManager
from ..websocket import WebsocketManager

router = APIRouter()

@router.post("/{ticket_id}/comments", response_model=TicketComment)
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

@router.get("/{ticket_id}/comments", response_model=List[TicketComment])
async def read_comments(ticket_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(TicketComment).where(text("ticket_id = :tid")).params(tid=ticket_id))
    return result.scalars().all()

@router.get("/{ticket_id}/comments/{comment_id}", response_model=TicketComment)
async def read_comment(ticket_id: int, comment_id: int, session: AsyncSession = Depends(get_session)):
    comment = await session.get(TicketComment, comment_id)
    if not comment or comment.ticket_id != ticket_id:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@router.put("/{ticket_id}/comments/{comment_id}", response_model=TicketComment)
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

@router.delete("/{ticket_id}/comments/{comment_id}", response_model=dict)
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
