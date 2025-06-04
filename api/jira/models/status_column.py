from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from .board import Board

if TYPE_CHECKING:
    from .ticket import Ticket

class StatusColumn(SQLModel, table=True):
    __tablename__ = "status_column"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    board_id: int = Field(foreign_key="board.id")
    board: Board = Relationship(back_populates="columns")
    tickets: List["Ticket"] = Relationship(back_populates="column")
    order: int = Field(default=0)