from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ...models.webhook import Webhook
from ..dependencies import get_session


async def create_webhook(webhook: Webhook, session: AsyncSession = Depends(get_session)):
    session.add(webhook)
    await session.commit()
    await session.refresh(webhook)
    return webhook
