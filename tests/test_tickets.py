import pytest

def test_create_ticket(client, test_uuid):
    """Test creating a ticket with a valid column."""
    # Create a board first
    board_response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column linked to the board
    column_response = client.post("/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Create a ticket linked to the column
    response = client.post("/tickets/", json={"title": "Test Ticket", "description": f"Test Description {test_uuid}", "column_id": column_id})
    assert response.status_code == 200
    assert response.json()["title"] == "Test Ticket"

def test_read_tickets(client, test_uuid):
    """Test reading all tickets."""
    board_response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    column_response = client.post("/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]
    client.post("/tickets/", json={"title": "Test Ticket", "description": f"Test Description {test_uuid}", "column_id": column_id})

    response = client.get("/tickets/")
    assert response.status_code == 200

def test_read_ticket(client, test_uuid):
    """Test reading a specific ticket by ID."""
    board_response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    column_response = client.post("/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]
    ticket_response = client.post("/tickets/", json={"title": "Test Ticket", "description": f"Test Description {test_uuid}", "column_id": column_id})
    ticket_id = ticket_response.json()["id"]

    response = client.get(f"/tickets/{ticket_id}")
    assert response.status_code == 200
    assert response.json()["id"] == ticket_id

def test_update_ticket(client, test_uuid):
    """Test updating a ticket."""
    board_response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    column_response = client.post("/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]
    ticket_response = client.post("/tickets/", json={"title": "Test Ticket", "description": f"Test Description {test_uuid}", "column_id": column_id})
    ticket_id = ticket_response.json()["id"]

    update_response = client.put(f"/tickets/{ticket_id}", json={"title": "Updated Ticket"})
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Ticket"

def test_delete_ticket(client, test_uuid):
    """Test deleting a ticket."""
    board_response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    column_response = client.post("/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]
    ticket_response = client.post("/tickets/", json={"title": "Test Ticket", "description": f"Test Description {test_uuid}", "column_id": column_id})
    ticket_id = ticket_response.json()["id"]

    delete_response = client.delete(f"/tickets/{ticket_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Ticket deleted successfully"