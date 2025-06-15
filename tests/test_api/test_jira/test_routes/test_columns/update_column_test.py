"""Tests for api/jira/routes/columns/update_column module."""

import pytest
from fastapi.testclient import TestClient
from tests.utils import get_unique_test_id


def test_update_column(client, test_uuid):
    """Test updating a column with a valid board."""
    # Create a board first
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column linked to the board
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Update the column
    update_response = client.put(f"/api/columns/{column_id}", json={"name": f"Updated Column-{test_uuid}"})
    assert update_response.status_code == 200
    assert update_response.json()["name"] == f"Updated Column-{test_uuid}"


def test_update_nonexistent_column(client, test_uuid):
    """Test updating a column that doesn't exist."""
    # Use an ID that shouldn't exist
    nonexistent_id = get_unique_test_id()
    update_data = {"name": f"Updated Nonexistent {test_uuid}"}
    
    response = client.put(f"/api/columns/{nonexistent_id}", json=update_data)
    
    # Verify error response
    assert response.status_code == 404
