"""Tests for api/jira/routes/columns/create_column module."""

import pytest
from fastapi.testclient import TestClient
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
