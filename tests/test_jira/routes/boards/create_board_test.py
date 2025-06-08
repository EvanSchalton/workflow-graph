from fastapi.testclient import TestClient
import pytest


def test_create_board(client, test_uuid):
    """Test creating a new board."""
    # Create a board
    board_data = {"name": f"Test Board {test_uuid}"}
    response = client.post("/api/boards/", json=board_data)
    
    # Verify response
    assert response.status_code == 200
    board = response.json()
    assert board["name"] == f"Test Board {test_uuid}"
    assert "id" in board
    
    # Verify the board was actually created by retrieving it
    get_response = client.get(f"/api/boards/{board['id']}")
    assert get_response.status_code == 200
    retrieved_board = get_response.json()
    assert retrieved_board["id"] == board["id"]
    assert retrieved_board["name"] == board["name"]


def test_create_board_invalid_data(client):
    """Test creating a board with invalid data."""
    # Try to create a board with missing required data
    response = client.post("/api/boards/", json={})
    
    # Verify error response
    assert response.status_code == 422  # Unprocessable Entity
