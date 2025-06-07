from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..dependencies import get_session
from ...models.status_column import StatusColumn


async def update_column(column_id: int, column: StatusColumn, session: AsyncSession = Depends(get_session)) -> StatusColumn:
    """Update a column."""
    existing_column = await session.get(StatusColumn, column_id)
    if not existing_column:
        raise HTTPException(status_code=404, detail="Column not found")
    for key, value in column.model_dump(exclude_unset=True).items():
        setattr(existing_column, key, value)
    session.add(existing_column)
    await session.commit()
    await session.refresh(existing_column)
    return existing_column
