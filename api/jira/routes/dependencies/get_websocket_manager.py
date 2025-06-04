from typing import TYPE_CHECKING
from fastapi import Request

if TYPE_CHECKING:
    from ...websocket import WebsocketManager

async def get_websocket_manager(request: Request) -> "WebsocketManager":
    return request.app.state.websocket_manager
