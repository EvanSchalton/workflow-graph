from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..dependencies import get_session
from ...models.status_column import StatusColumn


async def get_column_by_id(column_id: int, session: AsyncSession = Depends(get_session)) -> StatusColumn:
    """Get a column by ID."""
    column = await session.get(StatusColumn, column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    return column
