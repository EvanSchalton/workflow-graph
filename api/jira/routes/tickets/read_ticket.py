from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...models import Ticket
from ..dependencies import get_session


async def read_ticket(ticket_id: int, session: AsyncSession = Depends(get_session)):
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket
