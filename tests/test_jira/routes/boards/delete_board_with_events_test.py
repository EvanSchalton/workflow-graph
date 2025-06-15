from fastapi.testclient import TestClient
import pytest
from tests.utils import get_unique_test_id


def test_delete_board_with_events(client, test_uuid):
    """Test deleting a board with events."""
    # Create a test board first
    create_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = create_response.json()["id"]
    
    # Delete the board
    response = client.delete(f"/api/boards/{board_id}")
    
    # Verify response
    assert response.status_code == 200
    assert response.json()["message"] == "Board deleted successfully"
    
    # Verify the board was actually deleted
    get_response = client.get(f"/api/boards/{board_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_board(client):
    """Test deleting a board that doesn't exist."""
    # Use a board ID that is unlikely to exist
    nonexistent_id = get_unique_test_id()
    
    response = client.delete(f"/api/boards/{nonexistent_id}")
    
    # Verify error response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
