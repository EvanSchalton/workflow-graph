from sqlmodel import SQLModel, Field
from typing import Optional, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from .events.base_event import BaseEvent
from .webhook_event_code import WebhookEventCode
from pydantic import field_serializer, field_validator

class Webhook(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    event_code: WebhookEventCode

    async def publish(self, event: BaseEvent):
        # Logic to send the event payload to the subscriber's URL
        async with httpx.AsyncClient() as client:
            await client.post(
                self.url,
                json={
                    "webhook_id": self.id,
                    "event": {
                        "event_code": event.event_code.value,
                        "payload": event.payload.model_dump(),
                    }
                }
            )

    @field_serializer('event_code')
    def serialize_event_code(self, event_code: WebhookEventCode) -> str:
        return event_code.value

    @field_validator('event_code', mode='before')
    @classmethod
    def validate_event_code(cls, value):
        if isinstance(value, str):
            return WebhookEventCode(value)
        return value

class WebhookUpdate(SQLModel):
    url: Optional[str] = None
    event_code: Optional[WebhookEventCode] = None

    @field_validator('event_code', mode='before')
    @classmethod
    def validate_event_code(cls, value):
        if isinstance(value, str):
            return WebhookEventCode(value)
        return value