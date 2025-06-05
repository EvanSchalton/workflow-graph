from typing import List
from fastapi.websockets import WebSocket
from ..models.events.base_event import BaseEvent
from .connection import WebsocketConnection

class WebsocketManager:
    def __init__(self):
        self.active_connections: dict[int, WebsocketConnection] = {}

    async def connect(
        self,
        connection: WebsocketConnection,
    ) -> None:
        print(f"Attempting to connect WebSocket: {connection}")
        await connection.websocket.accept()
        self.active_connections[id(connection.websocket)] = connection
        print(f"WebSocket connected: {connection}")

    async def disconnect(self, connection: WebsocketConnection):
        print(f"Disconnecting: {connection}")
        del self.active_connections[id(connection.websocket)]

    async def broadcast(self, event: BaseEvent | str) -> None:
        if isinstance(event, BaseEvent):
            message = event.model_dump(mode="json")
        else:
            message = {"message": event}
        for connection in self.active_connections.values():
            # For string events, broadcast to all connections; for BaseEvent, check matches
            should_send = isinstance(event, str) or connection.matches(event)
            if should_send:
                try:
                    await connection.websocket.send_json(message)
                except Exception as e:
                    print(f"Error sending message: {e}")
                    await self.disconnect(connection)
        print(f"Broadcasted message: {message}")