"""Tests for api/jira/routes/boards/get_boards module."""

import pytest
from fastapi.testclient import TestClient


def test_read_boards(client):
    """Test reading all boards."""
    response = client.get("/api/boards/")
    assert response.status_code == 200
