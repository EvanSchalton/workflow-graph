from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from typing import List
from ..dependencies import get_session
from ...models.board import Board


async def get_boards(session: AsyncSession = Depends(get_session)) -> List[Board]:
    """Get all boards."""
    # We need to explicitly commit any pending changes to ensure they're visible
    # This is especially important in test environments
    await session.commit()
    
    # Execute the query to select all boards
    result = await session.execute(select(Board))
    boards = list(result.scalars().all())
    
    # Return all boards found
    return boards
