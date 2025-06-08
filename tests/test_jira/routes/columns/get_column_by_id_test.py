from fastapi.testclient import TestClient
import pytest


def test_get_column_by_id(client, test_uuid):
    """Test reading a specific column by ID."""
    # Create a board first
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    
    # Create a column linked to the board
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Test getting the column by ID
    response = client.get(f"/api/columns/{column_id}")
    
    # Verify response
    assert response.status_code == 200
    column = response.json()
    assert column["id"] == column_id
    assert column["name"] == f"Column-{test_uuid}"
    assert column["board_id"] == board_id


def test_get_column_by_id_not_found(client):
    """Test getting a non-existent column."""
    # Use an ID that shouldn't exist
    nonexistent_id = 99999
    response = client.get(f"/api/columns/{nonexistent_id}")
    
    # Should return a 404 error
    assert response.status_code == 404
