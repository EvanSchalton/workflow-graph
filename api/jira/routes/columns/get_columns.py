from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from typing import List
from ..dependencies import get_session
from ...models.status_column import StatusColumn


async def get_columns(session: AsyncSession = Depends(get_session)) -> List[StatusColumn]:
    """Get all columns."""
    result = await session.execute(select(StatusColumn))
    return list(result.scalars().all())
