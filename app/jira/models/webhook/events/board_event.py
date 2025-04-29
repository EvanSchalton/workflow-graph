from ...board import Board
from ..webhook_event_code import WebhookEventCode
from .base_event import BaseEvent

class BoardEvent(BaseEvent):
    def __init__(self, event_code: WebhookEventCode, payload: Board):
        super().__init__(event_code=event_code, payload=payload)