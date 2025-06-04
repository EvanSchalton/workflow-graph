from ..board import Board
from .base_event import BaseEvent

class BoardEvent(BaseEvent):
    payload: Board
