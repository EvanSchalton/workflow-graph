from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from ..dependencies import get_session
from ...models.ticket import Ticket


async def delete_ticket(ticket_id: int, session: AsyncSession = Depends(get_session)) -> Dict[str, str]:
    """Delete a ticket."""
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    await session.delete(ticket)
    await session.commit()
    return {"message": "Ticket deleted successfully"}
