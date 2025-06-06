from sqlmodel import SQLModel, Field
from typing import Optional
import httpx
from .events.base_event import BaseEvent
from .events.event_code import EventCode
from pydantic import field_serializer, field_validator

class Webhook(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    event_code: EventCode

    async def publish(self, event: BaseEvent):
        # Logic to send the event payload to the subscriber's URL
        async with httpx.AsyncClient() as client:
            await client.post(
                self.url,
                json={
                    "webhook_id": self.id,
                    "event": {
                        "event_code": event.event_code.value,
                        "payload": event.payload.model_dump(mode="json"),
                    }
                }
            )

    @field_serializer('event_code')
    def serialize_event_code(self, event_code: EventCode) -> str:
        return event_code.value

    @field_validator('event_code', mode='before')
    @classmethod
    def validate_event_code(cls, value):
        if isinstance(value, str):
            return EventCode(value)
        return value

class WebhookUpdate(SQLModel):
    url: Optional[str] = None
    event_code: Optional[EventCode] = None

    @field_validator('event_code', mode='before')
    @classmethod
    def validate_event_code(cls, value):
        if isinstance(value, str):
            return EventCode(value)
        return value