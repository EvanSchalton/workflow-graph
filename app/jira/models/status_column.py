from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from .board import Board

class StatusColumn(SQLModel, table=True):
    __tablename__ = "status_column"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    board_id: int = Field(foreign_key="board.id")
    board: Board = Relationship(back_populates="columns")
    tickets: List["Ticket"] = Relationship(back_populates="column")