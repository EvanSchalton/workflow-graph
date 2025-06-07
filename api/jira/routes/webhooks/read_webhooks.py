from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from ...models.webhook import Webhook
from ..dependencies import get_session


async def read_webhooks(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Webhook))
    return result.scalars().all()
