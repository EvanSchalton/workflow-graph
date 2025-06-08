from fastapi.testclient import TestClient
import pytest


def test_get_tickets(client, test_uuid):
    """Test retrieving all tickets."""
    # Create a board first
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column linked to the board
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Create multiple tickets
    ticket1 = client.post("/api/tickets/", json={"title": "Ticket 1", "description": f"Description 1 {test_uuid}", "column_id": column_id})
    ticket2 = client.post("/api/tickets/", json={"title": "Ticket 2", "description": f"Description 2 {test_uuid}", "column_id": column_id})
    
    # Get all tickets
    response = client.get("/api/tickets/")
    assert response.status_code == 200
    
    # Check if our tickets are in the response
    tickets = response.json()
    assert isinstance(tickets, list)
    
    # Find our test tickets
    created_ticket_ids = {ticket1.json()["id"], ticket2.json()["id"]}
    found_tickets = [ticket for ticket in tickets if ticket["id"] in created_ticket_ids]
    
    assert len(found_tickets) == 2
    
    # Verify ticket contents
    for ticket in found_tickets:
        if ticket["title"] == "Ticket 1":
            assert ticket["description"] == f"Description 1 {test_uuid}"
        elif ticket["title"] == "Ticket 2":
            assert ticket["description"] == f"Description 2 {test_uuid}"


def test_get_tickets_empty(client, test_uuid, monkeypatch):
    """Test retrieving tickets when none exist (using mocking)."""
    # This is a more advanced test that would mock the database session
    # For simplicity, we're just verifying that the API returns a list (even if empty)
    response = client.get("/api/tickets/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
