from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from typing import List
from ..dependencies import get_session
from ...models.ticket import Ticket


async def get_tickets(session: AsyncSession = Depends(get_session)) -> List[Ticket]:
    """Get all tickets."""
    result = await session.execute(select(Ticket))
    return list(result.scalars().all())
