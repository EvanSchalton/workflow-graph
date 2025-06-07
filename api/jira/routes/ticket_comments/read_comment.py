from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...models import TicketComment
from ..dependencies import get_session


async def read_comment(ticket_id: int, comment_id: int, session: AsyncSession = Depends(get_session)):
    comment = await session.get(TicketComment, comment_id)
    if not comment or comment.ticket_id != ticket_id:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment
