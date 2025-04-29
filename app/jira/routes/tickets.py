from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from typing import List
from ..models.ticket import Ticket
from ..routes.get_session import get_session

router = APIRouter()

@router.post("/", response_model=Ticket)
async def create_ticket(ticket: Ticket, session: AsyncSession = Depends(get_session)):
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    return ticket

@router.get("/", response_model=List[Ticket])
async def read_tickets(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Ticket))
    return result.scalars().all()

@router.get("/{ticket_id}", response_model=Ticket)
async def read_ticket(ticket_id: int, session: AsyncSession = Depends(get_session)):
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.put("/{ticket_id}", response_model=Ticket)
async def update_ticket(ticket_id: int, ticket: Ticket, session: AsyncSession = Depends(get_session)):
    existing_ticket = await session.get(Ticket, ticket_id)
    if not existing_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    for key, value in ticket.model_dump(exclude_unset=True).items():
        setattr(existing_ticket, key, value)
    session.add(existing_ticket)
    await session.commit()
    await session.refresh(existing_ticket)
    return existing_ticket

@router.delete("/{ticket_id}", response_model=dict)
async def delete_ticket(ticket_id: int, session: AsyncSession = Depends(get_session)):
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    await session.delete(ticket)
    await session.commit()
    return {"message": "Ticket deleted successfully"}