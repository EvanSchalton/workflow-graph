from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from typing import List
from ..dependencies import get_session
from ...models.board import Board


async def get_boards(session: AsyncSession = Depends(get_session)) -> List[Board]:
    """Get all boards."""
    result = await session.execute(select(Board))
    return list(result.scalars().all())
