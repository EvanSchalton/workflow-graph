from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Boolean
from .models import Webhook, WebhookEventCode
import asyncio

class WebhookBroadcaster:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_subscribers(self, event_code: WebhookEventCode):
        result = await self.session.execute(
            select(Webhook).where(cast(Webhook.event_code == event_code, Boolean))
        )
        return result.scalars().all()

    async def broadcast(self, event):
        subscribers = await self.get_subscribers(event.event_code)
        publish_tasks = [subscriber.publish(event=event) for subscriber in subscribers]
        await asyncio.gather(*publish_tasks)