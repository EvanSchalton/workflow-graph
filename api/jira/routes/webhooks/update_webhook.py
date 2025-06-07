from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...models.webhook import Webhook, WebhookUpdate
from ..dependencies import get_session


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
