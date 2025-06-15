"""Tests for api/jira/routes/tickets/get_tickets module."""

import pytest
from fastapi.testclient import TestClient


def test_read_tickets(client: TestClient, test_uuid: str) -> None:
    """Test reading all tickets."""
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]
    client.post("/api/tickets/", json={"title": "Test Ticket", "description": f"Test Description {test_uuid}", "column_id": column_id})

    response = client.get("/api/tickets/")
    assert response.status_code == 200
