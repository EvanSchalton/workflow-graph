from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .manager import WebsocketManager
from .connection import WebsocketConnection

router = APIRouter()

@router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket,
    board_id: int | None = None,
    ticket_id: int | None = None,
):
    print("WebSocket handshake started.")
    try:
        websocket_manager: WebsocketManager = websocket.app.state.websocket_manager
        print("websocket_manager retrieved successfully.")
    except AttributeError as e:
        print(f"Error accessing websocket_manager: {e}")
        raise

    print("websocket_endpoint: ", {
        "websocket": websocket,
        "board_id": board_id,
        "ticket_id": ticket_id,
    })

    try:
        connection = WebsocketConnection(
            websocket=websocket,
            board_id=board_id,
            ticket_id=ticket_id,
        )
        await websocket_manager.connect(connection)
        print("WebSocket connection established.")

        while True:
            data = await websocket.receive_json()
            print("Received data: ", data)
            await websocket_manager.broadcast(data)
    except WebSocketDisconnect:
        print("WebSocket disconnected.")
        await websocket_manager.disconnect(connection)
    except Exception as e:
        print(f"Unhandled exception in WebSocket route: {e}")
        raise
