from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class Board(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    columns: List["StatusColumn"] = Relationship(back_populates="board")