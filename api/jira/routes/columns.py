from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from typing import List
from ..models import StatusColumn, EventCode, StatusColumnEvent
from .dependencies import get_session, get_webhook_manager, get_websocket_manager
from ..webhook_manager import WebhookManager
from ..websocket import WebsocketManager

router = APIRouter()

@router.post("/", response_model=StatusColumn)
async def create_column(
    column: StatusColumn,
    session: AsyncSession = Depends(get_session),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
    websocket_manager: WebsocketManager = Depends(get_websocket_manager),
):
    session.add(column)
    event = StatusColumnEvent(
        event_code=EventCode.COLUMN_CREATE,
        payload=column
    )
    await webhook_manager.broadcast(event=event)
    await websocket_manager.broadcast(event=event)
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
    if column is None:
        raise HTTPException(status_code=404, detail="Column not found")
    return column

@router.put("/{column_id}", response_model=StatusColumn)
async def update_column(
    column_id: int,
    column: StatusColumn,
    session: AsyncSession = Depends(get_session),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
    websocket_manager: WebsocketManager = Depends(get_websocket_manager),
):
    existing_column = await session.get(StatusColumn, column_id)
    if existing_column is None:
        raise HTTPException(status_code=404, detail="Column not found")
    for key, value in column.model_dump(exclude_unset=True).items():
        setattr(existing_column, key, value)
    session.add(existing_column)
    event = StatusColumnEvent(event_code=EventCode.COLUMN_EDIT, payload=existing_column)
    await webhook_manager.broadcast(event=event)
    await websocket_manager.broadcast(event=event)
    await session.commit()
    await session.refresh(existing_column)
    return existing_column

@router.delete("/{column_id}", response_model=dict)
async def delete_column(
    column_id: int,
    session: AsyncSession = Depends(get_session),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
    websocket_manager: WebsocketManager = Depends(get_websocket_manager),
):
    column = await session.get(StatusColumn, column_id)
    if column is None:
        raise HTTPException(status_code=404, detail="Column not found")
    event = StatusColumnEvent(event_code=EventCode.COLUMN_DELETE, payload=column)
    await webhook_manager.broadcast(event=event)
    await websocket_manager.broadcast(event=event)
    await session.delete(column)
    await session.commit()
    return {"message": "Column deleted successfully"}