from ..webhook_event_code import WebhookEventCode
from sqlmodel import SQLModel

class BaseEvent:
    def __init__(self, event_code: WebhookEventCode, payload: SQLModel):
        self.event_code = event_code
        self.payload = payload