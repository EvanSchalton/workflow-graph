"""Tests for api/jira/routes/boards/get_board_by_id module."""

import pytest
from fastapi.testclient import TestClient


def test_read_board(client, test_uuid):
    """Test reading a specific board by ID."""
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    response = client.get(f"/api/boards/{board_id}")
    assert response.status_code == 200
    assert response.json()["id"] == board_id
