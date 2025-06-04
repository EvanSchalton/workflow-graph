from sqlmodel import SQLModel
from pydantic import BaseModel
from .event_code import EventCode

class BaseEvent(BaseModel):
    event_code: EventCode
    payload: SQLModel
