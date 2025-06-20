"""Tests for api/jira/routes/boards/create_board module."""

import pytest
from fastapi.testclient import TestClient


def test_create_board(client, test_uuid):
    """Test creating a board."""
    response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == f"Test Board {test_uuid}"
