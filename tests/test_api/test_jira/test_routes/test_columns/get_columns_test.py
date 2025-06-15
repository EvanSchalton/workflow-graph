"""Tests for api/jira/routes/columns/get_columns module."""

import pytest
from fastapi.testclient import TestClient


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
