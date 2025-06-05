import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.jira.websocket import WebsocketManager, WebsocketConnection
from api.jira.models.events.board_event import BoardEvent
from api.jira.models.events.event_code import EventCode
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture(scope="function")
def mock_websocket_manager(client: TestClient):
    """Create a mock websocket manager and replace the real one in app state."""
    from fastapi import FastAPI
    
    mock_manager = AsyncMock(spec=WebsocketManager)
    mock_manager.active_connections = {}
    
    # Mock the connect method to simulate adding to active connections
    async def mock_connect(connection):
        connection_id = id(connection.websocket)
        mock_manager.active_connections[connection_id] = connection
    
    mock_manager.connect.side_effect = mock_connect
    
    # Mock the broadcast method to just record the call
    async def mock_broadcast(event):
        pass  # Just record that it was called
    
    mock_manager.broadcast.side_effect = mock_broadcast
    
    # Replace the websocket manager in app state (cast to FastAPI for type checking)
    app: FastAPI = client.app  # type: ignore
    original_manager = getattr(app.state, 'websocket_manager', None)
    app.state.websocket_manager = mock_manager
    
    yield mock_manager
    
    # Restore original manager if it existed
    if original_manager is not None:
        app.state.websocket_manager = original_manager

def test_websocket_connect(client: TestClient, mock_websocket_manager: AsyncMock) -> None:
    """Test that a websocket connection can be established and manager methods are called."""
    with client.websocket_connect("/ws/?board_id=1") as websocket:
        assert websocket is not None
        
        # Send a test message to verify the connection works
        websocket.send_json({"test": "message"})
        
        # Verify that the websocket manager's connect method was called
        mock_websocket_manager.connect.assert_called_once()
        
        # Verify the connection was added to active connections
        connection_id = None
        for conn_id, conn in mock_websocket_manager.active_connections.items():
            if conn.board_id == 1 and conn.ticket_id is None:
                connection_id = conn_id
                break
        
        assert connection_id is not None, "Connection should be in active_connections"
        
        # Verify broadcast was called with the test message
        mock_websocket_manager.broadcast.assert_called_once_with({"test": "message"})

def test_websocket_connect_with_ticket_id(client: TestClient, mock_websocket_manager: AsyncMock) -> None:
    """Test websocket connection with both board_id and ticket_id."""
    with client.websocket_connect("/ws/?board_id=2&ticket_id=42") as websocket:
        assert websocket is not None
        
        # Verify connection was established with correct parameters
        mock_websocket_manager.connect.assert_called_once()
        
        # Check the connection object has the right parameters
        call_args = mock_websocket_manager.connect.call_args[0][0]  # First positional argument
        assert call_args.board_id == 2
        assert call_args.ticket_id == 42

# def test_websocket_broadcast(client: TestClient, websocket_manager: WebsocketManager) -> None:
#     with client.websocket_connect("/ws?board_id=1") as websocket:
#         event = BoardEvent(event_code=EventCode.BOARD_CREATE, payload={"board_id": 1})
#         websocket_manager.broadcast(event=event)  # No need to await since it's synchronous in this context
#         message = websocket.receive_json()  # Synchronous receive
#         assert message["event_code"] == EventCode.BOARD_CREATE.value
#         assert message["payload"]["board_id"] == 1