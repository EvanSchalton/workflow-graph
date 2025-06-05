from ..ticket_comment import TicketComment
from .base_event import BaseEvent

class TicketCommentEvent(BaseEvent):
    payload: TicketComment
