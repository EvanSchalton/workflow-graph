"""Tests for api/jira/routes/tickets/get_ticket_by_id module."""

import pytest
from fastapi.testclient import TestClient
from tests.utils import get_unique_test_id


def test_read_ticket(client: TestClient, test_uuid: str) -> None:
    """Test reading a specific ticket by ID."""
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]
    ticket_response = client.post("/api/tickets/", json={"title": "Test Ticket", "description": f"Test Description {test_uuid}", "column_id": column_id})
    ticket_id = ticket_response.json()["id"]

    response = client.get(f"/api/tickets/{ticket_id}")
    assert response.status_code == 200
    assert response.json()["id"] == ticket_id


def test_read_ticket_not_found(client: TestClient) -> None:
    """Test retrieving a non-existent ticket by ID."""
    # Use a ticket ID that is unlikely to exist
    nonexistent_id = get_unique_test_id()
    response = client.get(f"/api/tickets/{nonexistent_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
