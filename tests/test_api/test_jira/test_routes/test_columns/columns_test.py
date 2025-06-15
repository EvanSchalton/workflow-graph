# filepath: tests/test_api/test_jira/test_routes/test_columns/columns_test.py
"""
COMPLETE MIGRATION: columns_test.py
Source: tests/test_jira/columns_test.py
Migrated: 2025-06-15 19:35:42
Test Functions: 10
Status: COMPLETE - All content migrated
"""


# MIGRATED: Content moved to tests/test_api/test_jira/test_routes/test_columns/ (multiple files)
# This file is kept for reference but all tests have been migrated to the new structure
# Date: 2025-06-15
# Migration completed: 10 test functions migrated successfully to separate files

from fastapi.testclient import TestClient
import pytest
from tests.utils import get_unique_test_id


def test_create_column(client, test_uuid):
    """Test creating a column with a valid board."""
    # Create a board first
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column linked to the board
    response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    assert response.status_code == 200
    assert response.json()["name"] == f"Column-{test_uuid}"


def test_create_column_invalid_board(client, test_uuid):
    """Test creating a column with an invalid board ID."""
    # Use a board ID that is unlikely to exist
    invalid_board_id = get_unique_test_id()
    column_data = {"name": f"Invalid Board Column {test_uuid}", "board_id": invalid_board_id}
    
    response = client.post("/api/columns/", json=column_data)
    
    # The API should return an error
    assert response.status_code in (400, 404, 422)  # Depends on how the API handles invalid foreign keys


def test_read_columns(client, test_uuid):
    """Test reading all columns."""
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})

    response = client.get("/api/columns/")
    assert response.status_code == 200


def test_read_columns_empty(client):
    """Test reading columns when none exist."""
    response = client.get("/api/columns/")
    assert response.status_code == 200
    # Should return an empty list
    columns = response.json()
    assert isinstance(columns, list)


def test_read_column(client, test_uuid):
    """Test reading a specific column by ID."""
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    response = client.get(f"/api/columns/{column_id}")
    assert response.status_code == 200
    assert response.json()["id"] == column_id


def test_read_column_not_found(client):
    """Test getting a non-existent column."""
    # Use an ID that shouldn't exist
    nonexistent_id = get_unique_test_id()
    response = client.get(f"/api/columns/{nonexistent_id}")
    
    # Verify error response
    assert response.status_code == 404


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