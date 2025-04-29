from ..webhook_event_code import WebhookEventCode
from ...status_column import StatusColumn
from .base_event import BaseEvent

class StatusColumnEvent(BaseEvent):
    def __init__(self, event_code: WebhookEventCode, payload: StatusColumn):
        super().__init__(event_code=event_code, payload=payload)