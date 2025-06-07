from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..dependencies import get_session
from ...models.ticket import Ticket


async def update_ticket(ticket_id: int, ticket: Ticket, session: AsyncSession = Depends(get_session)) -> Ticket:
    """Update a ticket."""
    existing_ticket = await session.get(Ticket, ticket_id)
    if not existing_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    for key, value in ticket.model_dump(exclude_unset=True).items():
        setattr(existing_ticket, key, value)
    session.add(existing_ticket)
    await session.commit()
    await session.refresh(existing_ticket)
    return existing_ticket
