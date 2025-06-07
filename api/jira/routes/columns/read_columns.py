from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from ...models import StatusColumn
from ..dependencies import get_session


async def read_columns(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(StatusColumn))
    return result.scalars().all()
