from fastapi import FastAPI, APIRouter
from .routes import (
    board_router,
    column_router,
    ticket_router,
    webhook_router,
)
from .routes.mcp import router as mcp_router
from .lifespan import lifespan, DATABASE_URL
from .websocket import websocket_router


app = FastAPI(lifespan=lifespan)

api = APIRouter()
api.include_router(board_router, prefix="/boards")
api.include_router(column_router, prefix="/columns")
api.include_router(ticket_router, prefix="/tickets")
api.include_router(webhook_router, prefix="/webhooks")

app.include_router(api, prefix="/api")
app.include_router(mcp_router, prefix="/mcp")

print("Registering WebSocket route at /ws")
app.add_api_websocket_route("/ws", websocket_router)

__all__ = [
    "app",
    "DATABASE_URL",
]