"""Tests for the get_boards endpoint."""
import pytest
from fastapi.testclient import TestClient


def test_get_boards_empty(client):
    """Test getting boards when none exist (or no test boards exist yet)."""
    # This may not be an empty list in a shared test DB, but we can at least check the response type
    response = client.get("/api/boards/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_boards_with_created_boards(client, test_uuid):
    """Test getting boards after creating some."""
    # Create test boards
    board1_data = {"name": f"First Board {test_uuid}"}
    board2_data = {"name": f"Second Board {test_uuid}"}
    
    board1_response = client.post("/api/boards/", json=board1_data)
    board2_response = client.post("/api/boards/", json=board2_data)
    
    board1_id = board1_response.json()["id"]
    board2_id = board2_response.json()["id"]
    
    # Get all boards
    response = client.get("/api/boards/")
    assert response.status_code == 200
    boards = response.json()
    
    # Verify our test boards are in the response
    board1_found = any(b["id"] == board1_id and b["name"] == f"First Board {test_uuid}" for b in boards)
    board2_found = any(b["id"] == board2_id and b["name"] == f"Second Board {test_uuid}" for b in boards)
    
    assert board1_found, f"First board with ID {board1_id} not found in response"
    assert board2_found, f"Second board with ID {board2_id} not found in response"
