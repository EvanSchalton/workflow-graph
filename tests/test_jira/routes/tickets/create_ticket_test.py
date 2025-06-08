from fastapi.testclient import TestClient
import pytest


def test_create_ticket(client, test_uuid):
    """Test creating a ticket with valid data."""
    # Create a board first
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column linked to the board
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Create a ticket linked to the column
    ticket_data = {
        "title": "New Test Ticket",
        "description": f"Test Description {test_uuid}",
        "column_id": column_id
    }
    response = client.post("/api/tickets/", json=ticket_data)
    
    assert response.status_code == 200
    ticket = response.json()
    assert ticket["title"] == "New Test Ticket"
    assert ticket["description"] == f"Test Description {test_uuid}"
    assert ticket["column_id"] == column_id
    assert "id" in ticket
    
    # Verify the ticket was actually created by retrieving it
    get_response = client.get(f"/api/tickets/{ticket['id']}")
    assert get_response.status_code == 200


def test_create_ticket_invalid_column(client, test_uuid):
    """Test creating a ticket with an invalid column ID."""
    # Try to create a ticket with a non-existent column
    invalid_column_id = 999999  # Assume this ID doesn't exist
    ticket_data = {
        "title": "Invalid Column Ticket",
        "description": f"Test Description {test_uuid}",
        "column_id": invalid_column_id
    }
    
    response = client.post("/api/tickets/", json=ticket_data)
    
    # The API should return an error
    assert response.status_code in (400, 404, 422)  # Depends on how the API handles invalid foreign keys
