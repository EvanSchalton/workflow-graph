"""Tests for api/jira/routes/tickets/create_ticket module."""

import pytest
from fastapi.testclient import TestClient
from tests.utils import get_unique_test_id


def test_create_ticket(client: TestClient, test_uuid: str) -> None:
    """Test creating a ticket with a valid column."""
    # Create a board first
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column linked to the board
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Create a ticket linked to the column
    response = client.post("/api/tickets/", json={"title": "Test Ticket", "description": f"Test Description {test_uuid}", "column_id": column_id})
    assert response.status_code == 200
    assert response.json()["title"] == "Test Ticket"


def test_create_ticket_invalid_column(client: TestClient, test_uuid: str) -> None:
    """Test creating a ticket with an invalid column ID."""
    # Try to create a ticket with a non-existent column
    invalid_column_id = get_unique_test_id()  # Use unique ID that doesn't exist
    ticket_data = {
        "title": "Invalid Column Ticket",
        "description": f"Test Description {test_uuid}",
        "column_id": invalid_column_id
    }
    
    response = client.post("/api/tickets/", json=ticket_data)
    
    # The API should return an error
    assert response.status_code in (400, 404, 422)  # Depends on how the API handles invalid foreign keys
