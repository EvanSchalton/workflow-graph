from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
import pytest


def test_get_ticket_by_id(client, test_uuid):
    """Test retrieving a specific ticket by ID."""
    # Create a board first
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column linked to the board
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Create a ticket linked to the column
    ticket_response = client.post("/api/tickets/", json={"title": "Test Ticket", "description": f"Test Description {test_uuid}", "column_id": column_id})
    ticket_id = ticket_response.json()["id"]

    # Test retrieving the ticket by ID
    response = client.get(f"/api/tickets/{ticket_id}")
    assert response.status_code == 200
    assert response.json()["id"] == ticket_id
    assert response.json()["title"] == "Test Ticket"
    assert response.json()["description"] == f"Test Description {test_uuid}"


def test_get_ticket_by_id_not_found(client):
    """Test retrieving a non-existent ticket by ID."""
    # Use a ticket ID that is unlikely to exist
    nonexistent_id = 99999
    response = client.get(f"/api/tickets/{nonexistent_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
