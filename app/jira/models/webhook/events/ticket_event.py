from ..webhook_event_code import WebhookEventCode
from ...ticket import Ticket
from .base_event import BaseEvent

class TicketEvent(BaseEvent):
    def __init__(self, event_code: WebhookEventCode, payload: Ticket):
        super().__init__(event_code=event_code, payload=payload)