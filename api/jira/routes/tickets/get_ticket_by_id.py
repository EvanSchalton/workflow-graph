from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..dependencies import get_session
from ...models.ticket import Ticket


async def get_ticket_by_id(ticket_id: int, session: AsyncSession = Depends(get_session)) -> Ticket:
    """Get a ticket by ID."""
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket
