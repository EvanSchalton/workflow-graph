from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from .status_column import StatusColumn

if TYPE_CHECKING:
    from .ticket_comment import TicketComment

class Ticket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str]
    assignee: Optional[str]
    conversation: Optional[str]
    column_id: int = Field(foreign_key="status_column.id")
    column: StatusColumn = Relationship(back_populates="tickets")
    comments: List["TicketComment"] = Relationship(back_populates="ticket")