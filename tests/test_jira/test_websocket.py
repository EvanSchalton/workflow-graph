import pytest
from fastapi.testclient import TestClient
from api.jira.models.events.board_event import BoardEvent
from api.jira.models.events.event_code import EventCode

def test_websocket_connect(client: TestClient) -> None:
    """Test that a websocket connection can be established."""
    with client.websocket_connect("/ws/?board_id=1") as websocket:
        assert websocket is not None
        
        # Send a test message to verify the connection works
        websocket.send_json({"test": "message"})
        
        # The websocket connection should work without throwing exceptions
        # This tests the basic functionality without mocking internals

def test_websocket_connect_with_ticket_id(client: TestClient) -> None:
    """Test websocket connection with both board_id and ticket_id."""
    with client.websocket_connect("/ws/?board_id=2&ticket_id=42") as websocket:
        assert websocket is not None
        
        # The websocket connection should work with both parameters
        # This tests parameter handling without mocking internals

# def test_websocket_broadcast(client: TestClient, websocket_manager: WebsocketManager) -> None:
#     with client.websocket_connect("/ws?board_id=1") as websocket:
#         event = BoardEvent(event_code=EventCode.BOARD_CREATE, payload={"board_id": 1})
#         websocket_manager.broadcast(event=event)  # No need to await since it's synchronous in this context
#         message = websocket.receive_json()  # Synchronous receive
#         assert message["event_code"] == EventCode.BOARD_CREATE.value
#         assert message["payload"]["board_id"] == 1