from fastapi.testclient import TestClient
import pytest


def test_get_board_by_id(client, test_uuid):
    """Test retrieving a specific board by ID."""
    # Create a test board first
    create_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = create_response.json()["id"]
    
    # Retrieve the board by ID
    response = client.get(f"/api/boards/{board_id}")
    
    # Verify response
    assert response.status_code == 200
    board = response.json()
    assert board["id"] == board_id
    assert board["name"] == f"Test Board {test_uuid}"


def test_get_board_by_id_not_found(client):
    """Test retrieving a non-existent board by ID."""
    # Use a board ID that is unlikely to exist
    nonexistent_id = 99999
    response = client.get(f"/api/boards/{nonexistent_id}")
    
    # Verify error response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
