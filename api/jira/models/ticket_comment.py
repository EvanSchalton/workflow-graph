from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .ticket import Ticket

class TicketComment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ticket_id: int = Field(foreign_key="ticket.id")
    ticket: "Ticket" = Relationship(back_populates="comments")
    author: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
