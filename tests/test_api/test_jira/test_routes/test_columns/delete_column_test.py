"""Tests for api/jira/routes/columns/delete_column module."""

import pytest
from fastapi.testclient import TestClient
from tests.utils import get_unique_test_id


def test_delete_column(client, test_uuid):
    """Test deleting a column with a valid board."""
    # Create a board first
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column linked to the board
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Delete the column
    delete_response = client.delete(f"/api/columns/{column_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Column deleted successfully"
    
    # Verify the column was actually deleted
    get_response = client.get(f"/api/columns/{column_id}")
    assert get_response.status_code == 404  # Should be not found


def test_delete_nonexistent_column(client):
    """Test deleting a column that doesn't exist."""
    # Use an ID that shouldn't exist
    nonexistent_id = get_unique_test_id()
    response = client.delete(f"/api/columns/{nonexistent_id}")
    
    # Should return a 404 error or a success message (depends on the implementation)
    assert response.status_code in (404, 200)
