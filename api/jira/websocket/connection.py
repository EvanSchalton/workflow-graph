from fastapi.websockets import WebSocket
from ..models.events.base_event import BaseEvent
from ..models import BoardEvent, TicketEvent, Board, Ticket
from pydantic import BaseModel, ConfigDict

class WebsocketConnection(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    websocket: WebSocket
    board_id: int | None = None
    ticket_id: int | None = None

    def matches(self, event: BaseEvent) -> bool:
        if self.board_id is None and self.ticket_id is None:
            return True
        
        if isinstance(event, BoardEvent):
            board: Board = event.payload
            if self.board_id is not None and self.board_id != board.id:
                return False
            
        if isinstance(event, TicketEvent):
            ticket: Ticket = event.payload
            if self.ticket_id is not None and self.ticket_id != ticket.id:
                return False
            if self.board_id is not None and self.board_id != ticket.column.board_id:
                return False
            
        return True