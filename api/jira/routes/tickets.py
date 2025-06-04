from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.sql import select
from typing import List
from ..models import Ticket, EventCode, TicketEvent
from sqlalchemy.orm import Session
from .dependencies import get_session, get_webhook_manager, get_websocket_manager
from ..webhook_manager import WebhookManager
from ..websocket import WebsocketManager

router = APIRouter()

@router.post("/", response_model=Ticket)
async def create_ticket(
    ticket: Ticket,
    session: Session = Depends(get_session),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
    websocket_manager: WebsocketManager = Depends(get_websocket_manager),
):
    session.add(ticket)
    event = TicketEvent(event_code=EventCode.TICKET_CREATE, payload=ticket)
    await webhook_manager.broadcast(event=event)
    await websocket_manager.broadcast(event=event)
    await session.commit()
    await session.refresh(ticket)
    return ticket

@router.get("/", response_model=List[Ticket])
async def read_tickets(session: Session = Depends(get_session)):
    result = await session.execute(select(Ticket))
    return result.scalars().all()

@router.get("/{ticket_id}", response_model=Ticket)
async def read_ticket(ticket_id: int, session: Session = Depends(get_session)):
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.put("/{ticket_id}", response_model=Ticket)
async def update_ticket(
    ticket_id: int,
    ticket: Ticket,
    session: Session = Depends(get_session),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
    websocket_manager: WebsocketManager = Depends(get_websocket_manager),
):
    existing_ticket = await session.get(Ticket, ticket_id)
    if not existing_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    for key, value in ticket.model_dump(exclude_unset=True).items():
        setattr(existing_ticket, key, value)
    session.add(existing_ticket)
    event=TicketEvent(event_code=EventCode.TICKET_EDIT, payload=ticket)
    await webhook_manager.broadcast(event=event)
    await websocket_manager.broadcast(event=event)
    await session.commit()
    await session.refresh(existing_ticket)
    return existing_ticket

@router.delete("/{ticket_id}", response_model=dict)
async def delete_ticket(
    ticket_id: int,
    session: Session = Depends(get_session),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
    websocket_manager: WebsocketManager = Depends(get_websocket_manager),
):
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    event = TicketEvent(event_code=EventCode.TICKET_DELETE, payload=ticket)
    await webhook_manager.broadcast(event=event)
    await websocket_manager.broadcast(event=event)
    await session.delete(ticket)
    await session.commit()
    return {"message": "Ticket deleted successfully"}