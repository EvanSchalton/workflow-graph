from ..ticket import Ticket
from .base_event import BaseEvent

class TicketEvent(BaseEvent):
    payload: Ticket