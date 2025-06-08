"""Tests for the create_board endpoint."""
import pytest
from fastapi.testclient import TestClient


def test_create_board_success(client, test_uuid):
    """Test successfully creating a board."""
    board_data = {"name": f"Test Board {test_uuid}"}
    response = client.post("/api/boards/", json=board_data)
    
    assert response.status_code == 200
    board = response.json()
    assert board["name"] == f"Test Board {test_uuid}"
    assert "id" in board
    
    # Verify the board was created
    board_id = board["id"]
    get_response = client.get(f"/api/boards/{board_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == f"Test Board {test_uuid}"


def test_create_board_validation_error(client):
    """Test creating a board with invalid data."""
    # Missing required name field
    response = client.post("/api/boards/", json={})
    assert response.status_code == 422  # Unprocessable Entity


def test_create_board_with_id(client, test_uuid):
    """Test creating a board with a specific ID."""
    # Creating a board with an ID should work, but the ID might be ignored
    # as the server typically assigns its own IDs
    board_data = {"name": f"Board with ID {test_uuid}", "id": 9999}
    response = client.post("/api/boards/", json=board_data)
    
    assert response.status_code == 200
    board = response.json()
    assert board["name"] == f"Board with ID {test_uuid}"
    # The ID might not match what we provided as the server may assign its own ID
    assert "id" in board
