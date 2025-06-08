from fastapi.testclient import TestClient
import pytest


def test_update_board(client, test_uuid):
    """Test updating an existing board."""
    # Create a test board first
    create_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = create_response.json()["id"]
    
    # Update the board
    updated_data = {"name": f"Updated Board {test_uuid}"}
    response = client.put(f"/api/boards/{board_id}", json=updated_data)
    
    # Verify response
    assert response.status_code == 200
    updated_board = response.json()
    assert updated_board["id"] == board_id
    assert updated_board["name"] == f"Updated Board {test_uuid}"
    
    # Verify the update was persisted
    get_response = client.get(f"/api/boards/{board_id}")
    assert get_response.status_code == 200
    retrieved_board = get_response.json()
    assert retrieved_board["name"] == f"Updated Board {test_uuid}"


def test_update_nonexistent_board(client, test_uuid):
    """Test updating a board that doesn't exist."""
    # Use a board ID that is unlikely to exist
    nonexistent_id = 99999
    updated_data = {"name": f"Updated Nonexistent {test_uuid}"}
    
    response = client.put(f"/api/boards/{nonexistent_id}", json=updated_data)
    
    # Verify error response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
