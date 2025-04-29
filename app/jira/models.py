from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class Board(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    columns: List["StatusColumn"] = Relationship(back_populates="board")

class StatusColumn(SQLModel, table=True):
    __tablename__ = "status_column"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    board_id: int = Field(foreign_key="board.id")
    board: Board = Relationship(back_populates="columns")
    tickets: List["Ticket"] = Relationship(back_populates="column")

class Ticket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str]
    assignee: Optional[str]
    conversation: Optional[str]
    column_id: int = Field(foreign_key="status_column.id")
    column: StatusColumn = Relationship(back_populates="tickets")

class Webhook(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    event: str