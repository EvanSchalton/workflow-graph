from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from typing import List
from ..models.webhook import Webhook, WebhookUpdate
from .dependencies import get_session

router = APIRouter()

@router.post("/", response_model=Webhook)
async def create_webhook(webhook: Webhook, session: AsyncSession = Depends(get_session)):
    session.add(webhook)
    await session.commit()
    await session.refresh(webhook)
    return webhook

@router.get("/", response_model=List[Webhook])
async def read_webhooks(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Webhook))
    return result.scalars().all()

@router.get("/{webhook_id}", response_model=Webhook)
async def read_webhook(webhook_id: int, session: AsyncSession = Depends(get_session)):
    webhook = await session.get(Webhook, webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return webhook

@router.put("/{webhook_id}", response_model=Webhook)
async def update_webhook(webhook_id: int, webhook: WebhookUpdate, session: AsyncSession = Depends(get_session)):
    existing_webhook = await session.get(Webhook, webhook_id)
    if not existing_webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    for key, value in webhook.model_dump(exclude_unset=True).items():
        setattr(existing_webhook, key, value)
    session.add(existing_webhook)
    await session.commit()
    await session.refresh(existing_webhook)
    return existing_webhook

@router.delete("/{webhook_id}", response_model=dict)
async def delete_webhook(webhook_id: int, session: AsyncSession = Depends(get_session)):
    webhook = await session.get(Webhook, webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    await session.delete(webhook)
    await session.commit()
    return {"message": "Webhook deleted successfully"}