from fastapi.testclient import TestClient
import pytest


def test_delete_column(client, test_uuid):
    """Test deleting a column."""
    # Create a board first
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    
    # Create a column linked to the board
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Delete the column
    response = client.delete(f"/api/columns/{column_id}")
    
    # Verify response
    assert response.status_code == 200
    
    # Verify the column was actually deleted
    get_response = client.get(f"/api/columns/{column_id}")
    assert get_response.status_code == 404  # Should be not found


def test_delete_nonexistent_column(client):
    """Test deleting a column that doesn't exist."""
    # Use an ID that shouldn't exist
    nonexistent_id = 99999
    response = client.delete(f"/api/columns/{nonexistent_id}")
    
    # Should return a 404 error or a success message (depends on the implementation)
    assert response.status_code in (404, 200)
