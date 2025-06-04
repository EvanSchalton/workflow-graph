import pytest
from fastapi.testclient import TestClient
from api.jira.websocket import WebsocketManager, WebsocketConnection
from api.jira.models.events.board_event import BoardEvent
from api.jira.models.events.event_code import EventCode
from unittest.mock import AsyncMock

@pytest.fixture(scope="function")
def websocket_manager(client: TestClient) -> WebsocketManager:
    # Patch the websocket_manager in app.state
    mock_websocket_manager = AsyncMock(spec=WebsocketManager)
    client.app.state.websocket_manager = mock_websocket_manager
    return mock_websocket_manager

def test_websocket_connect(client: TestClient, websocket_manager: WebsocketManager) -> None:
    assert websocket_manager is not None
    with client.websocket_connect("/ws?board_id=1") as websocket:
        assert websocket is not None
        assert id(websocket) in websocket_manager.active_connections

# def test_websocket_broadcast(client: TestClient, websocket_manager: WebsocketManager) -> None:
#     with client.websocket_connect("/ws?board_id=1") as websocket:
#         event = BoardEvent(event_code=EventCode.BOARD_CREATE, payload={"board_id": 1})
#         websocket_manager.broadcast(event=event)  # No need to await since it's synchronous in this context
#         message = websocket.receive_json()  # Synchronous receive
#         assert message["event_code"] == EventCode.BOARD_CREATE.value
#         assert message["payload"]["board_id"] == 1