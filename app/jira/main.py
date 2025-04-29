from fastapi import FastAPI
from .routes import (
    board_router,
    column_router,
    ticket_router,
    webhook_router,
)
from .lifespan import lifespan, DATABASE_URL

app = FastAPI(lifespan=lifespan)

app.include_router(board_router, prefix="/boards")
app.include_router(column_router, prefix="/columns")
app.include_router(ticket_router, prefix="/tickets")
app.include_router(webhook_router, prefix="/webhooks")

__all__ = [
    "app",
    "DATABASE_URL",
]