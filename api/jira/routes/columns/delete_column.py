from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from ..dependencies import get_session
from ...models.status_column import StatusColumn


async def delete_column(column_id: int, session: AsyncSession = Depends(get_session)) -> Dict[str, str]:
    """Delete a column."""
    column = await session.get(StatusColumn, column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    await session.delete(column)
    await session.commit()
    return {"message": "Column deleted successfully"}
