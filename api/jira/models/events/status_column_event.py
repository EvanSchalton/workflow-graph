from ..status_column import StatusColumn
from .base_event import BaseEvent

class StatusColumnEvent(BaseEvent):
    payload: StatusColumn