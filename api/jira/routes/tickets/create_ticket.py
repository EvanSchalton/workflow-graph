from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from ...models import Ticket, EventCode, TicketEvent, StatusColumn
from ..dependencies import get_session, get_webhook_manager, get_websocket_manager
from ...webhook_manager import WebhookManager
from ...websocket import WebsocketManager


async def create_ticket(
    ticket: Ticket,
    session: AsyncSession = Depends(get_session),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
    websocket_manager: WebsocketManager = Depends(get_websocket_manager),
):
    # Validate required fields
    if not ticket.title or not ticket.title.strip():
        raise HTTPException(status_code=422, detail="Ticket title is required")
    
    # Check if the column_id exists
    if ticket.column_id:
        result = await session.execute(select(StatusColumn).where(StatusColumn.id == ticket.column_id))
        column = result.scalar_one_or_none()
        if not column:
            raise HTTPException(status_code=404, detail=f"Column with ID {ticket.column_id} not found")
    else:
        raise HTTPException(status_code=422, detail="column_id is required")
    
    session.add(ticket)
    event = TicketEvent(event_code=EventCode.TICKET_CREATE, payload=ticket)
    await webhook_manager.broadcast(event=event)
    await websocket_manager.broadcast(event=event)
    await session.commit()
    await session.refresh(ticket)
    return ticket
