from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...models.webhook import Webhook
from ..dependencies import get_session


async def read_webhook(webhook_id: int, session: AsyncSession = Depends(get_session)):
    webhook = await session.get(Webhook, webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return webhook
