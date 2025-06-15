"""Tests for the Board API endpoints."""
import pytest
from fastapi.testclient import TestClient
from tests.utils import get_unique_test_id


def test_create_board(client, test_uuid):
    """Test creating a board."""
    board_data = {"name": f"Test Board {test_uuid}"}
    response = client.post("/api/boards/", json=board_data)
    
    assert response.status_code == 200
    board = response.json()
    assert board["name"] == f"Test Board {test_uuid}"
    assert "id" in board
    
    # Verify we can retrieve the board
    board_id = board["id"]
    get_response = client.get(f"/api/boards/{board_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == board_id


def test_create_board_invalid_data(client):
    """Test creating a board with invalid data."""
    # Try to create a board with missing required data
    response = client.post("/api/boards/", json={})
    
    # Verify error response
    assert response.status_code == 422  # Unprocessable Entity


def test_create_board_with_id(client, test_uuid):
    """Test creating a board with a specific ID."""
    # Creating a board with an ID should work, but the ID might be ignored
    # as the server typically assigns its own IDs
    unique_id = get_unique_test_id()
    board_data = {"name": f"Board with ID {test_uuid}", "id": unique_id}
    response = client.post("/api/boards/", json=board_data)
    
    assert response.status_code == 200
    board = response.json()
    assert board["name"] == f"Board with ID {test_uuid}"
    # The ID might not match what we provided as the server may assign its own ID
    assert "id" in board


def test_get_boards(client, test_uuid):
    """Test retrieving all boards."""
    # Create two test boards
    board1_data = {"name": f"Board One {test_uuid}"}
    board2_data = {"name": f"Board Two {test_uuid}"}
    
    response1 = client.post("/api/boards/", json=board1_data)
    response2 = client.post("/api/boards/", json=board2_data)
    
    board1_id = response1.json()["id"]
    board2_id = response2.json()["id"]
    
    # Get all boards
    get_all_response = client.get("/api/boards/")
    assert get_all_response.status_code == 200
    
    # Find our test boards in the response
    boards = get_all_response.json()
    assert isinstance(boards, list)
    
    # Find board1 in the response
    board1 = next((b for b in boards if b["id"] == board1_id), None)
    assert board1 is not None, f"Board with ID {board1_id} not found in API response"
    assert board1["name"] == f"Board One {test_uuid}"
    
    # Find board2 in the response
    board2 = next((b for b in boards if b["id"] == board2_id), None)  
    assert board2 is not None, f"Board with ID {board2_id} not found in API response"
    assert board2["name"] == f"Board Two {test_uuid}"


def test_get_board_by_id(client, test_uuid):
    """Test retrieving a specific board by ID."""
    # Create a board first
    board_data = {"name": f"Test Board {test_uuid}"}
    create_response = client.post("/api/boards/", json=board_data)
    board_id = create_response.json()["id"]
    
    # Retrieve the board
    get_response = client.get(f"/api/boards/{board_id}")
    assert get_response.status_code == 200
    
    # Verify the board data
    board = get_response.json()
    assert board["id"] == board_id
    assert board["name"] == f"Test Board {test_uuid}"


def test_get_board_by_id_not_found(client):
    """Test retrieving a non-existent board by ID."""
    # Use a board ID that is unlikely to exist
    nonexistent_id = get_unique_test_id()
    response = client.get(f"/api/boards/{nonexistent_id}")
    
    # Verify error response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_board(client, test_uuid):
    """Test updating a board."""
    # Create a board first
    original_name = f"Original Board {test_uuid}"
    board_data = {"name": original_name}
    create_response = client.post("/api/boards/", json=board_data)
    board_id = create_response.json()["id"]
    
    # Update the board
    updated_name = f"Updated Board {test_uuid}"
    update_data = {"name": updated_name}
    update_response = client.put(f"/api/boards/{board_id}", json=update_data)
    
    assert update_response.status_code == 200
    updated_board = update_response.json()
    assert updated_board["id"] == board_id
    assert updated_board["name"] == updated_name
    
    # Verify the update by retrieving the board again
    get_response = client.get(f"/api/boards/{board_id}")
    assert get_response.status_code == 200
    retrieved_board = get_response.json()
    assert retrieved_board["name"] == updated_name


def test_update_nonexistent_board(client, test_uuid):
    """Test updating a board that doesn't exist."""
    # Use a board ID that is unlikely to exist
    nonexistent_id = get_unique_test_id()
    updated_data = {"name": f"Updated Nonexistent {test_uuid}"}
    
    response = client.put(f"/api/boards/{nonexistent_id}", json=updated_data)
    
    # Verify error response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_board(client, test_uuid):
    """Test deleting a board."""
    # Create a board first
    board_data = {"name": f"Board to Delete {test_uuid}"}
    create_response = client.post("/api/boards/", json=board_data)
    board_id = create_response.json()["id"]
    
    # Delete the board
    delete_response = client.delete(f"/api/boards/{board_id}")
    assert delete_response.status_code == 200
    
    # Verify the board was deleted
    get_response = client.get(f"/api/boards/{board_id}")
    assert get_response.status_code == 404  # Not found
