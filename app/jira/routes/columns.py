from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from typing import List
from ..models.status_column import StatusColumn
from ..routes.get_session import get_session
from ..webhook_broadcaster import WebhookBroadcaster
from ..models.webhook import WebhookEventCode, StatusColumnEvent

router = APIRouter()

@router.post("/", response_model=StatusColumn)
async def create_column(column: StatusColumn, session: AsyncSession = Depends(get_session)):
    session.add(column)
    await WebhookBroadcaster(session).broadcast(StatusColumnEvent(WebhookEventCode.COLUMN_CREATE, column))
    await session.commit()
    await session.refresh(column)
    return column

@router.get("/", response_model=List[StatusColumn])
async def read_columns(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(StatusColumn))
    return result.scalars().all()

@router.get("/{column_id}", response_model=StatusColumn)
async def read_column(column_id: int, session: AsyncSession = Depends(get_session)):
    column = await session.get(StatusColumn, column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    return column

@router.put("/{column_id}", response_model=StatusColumn)
async def update_column(column_id: int, column: StatusColumn, session: AsyncSession = Depends(get_session)):
    existing_column = await session.get(StatusColumn, column_id)
    if not existing_column:
        raise HTTPException(status_code=404, detail="Column not found")
    for key, value in column.model_dump(exclude_unset=True).items():
        setattr(existing_column, key, value)
    session.add(existing_column)
    await WebhookBroadcaster(session).broadcast(event=StatusColumnEvent(event_code=WebhookEventCode.COLUMN_EDIT, payload=column))
    await session.commit()
    await session.refresh(existing_column)
    return existing_column

@router.delete("/{column_id}", response_model=dict)
async def delete_column(column_id: int, session: AsyncSession = Depends(get_session)):
    column = await session.get(StatusColumn, column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    await WebhookBroadcaster(session).broadcast(event=StatusColumnEvent(event_code=WebhookEventCode.COLUMN_DELETE, payload=column))
    await session.delete(column)
    await session.commit()
    return {"message": "Column deleted successfully"}