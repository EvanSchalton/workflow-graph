from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, text
from ...models import TicketComment
from ..dependencies import get_session


async def read_comments(ticket_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(TicketComment).where(text("ticket_id = :tid")).params(tid=ticket_id))
    return result.scalars().all()
