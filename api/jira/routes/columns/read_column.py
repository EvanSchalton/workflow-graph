from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...models import StatusColumn
from ..dependencies import get_session


async def read_column(column_id: int, session: AsyncSession = Depends(get_session)):
    column = await session.get(StatusColumn, column_id)
    if column is None:
        raise HTTPException(status_code=404, detail="Column not found")
    return column
