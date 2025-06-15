"""Tests for api/jira/routes/columns/get_column_by_id module."""

import pytest
from fastapi.testclient import TestClient
from tests.utils import get_unique_test_id


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
