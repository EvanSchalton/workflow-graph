import pytest

def test_create_board(client, test_uuid):
    """Test creating a board."""
    response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == f"Test Board {test_uuid}"

def test_read_boards(client):
    """Test reading all boards."""
    response = client.get("/boards/")
    assert response.status_code == 200

def test_read_board(client, test_uuid):
    """Test reading a specific board by ID."""
    board_response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    response = client.get(f"/boards/{board_id}")
    assert response.status_code == 200
    assert response.json()["id"] == board_id

def test_delete_board(client, test_uuid):
    """Test deleting a board."""
    # Create a board first
    board_response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Delete the board
    delete_response = client.delete(f"/boards/{board_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Board deleted successfully"