
from fastapi.testclient import TestClient
import pytest
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


def test_read_tickets(client: TestClient, test_uuid: str) -> None:
    """Test reading all tickets."""
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]
    client.post("/api/tickets/", json={"title": "Test Ticket", "description": f"Test Description {test_uuid}", "column_id": column_id})

    response = client.get("/api/tickets/")
    assert response.status_code == 200

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


def test_update_ticket(client: TestClient, test_uuid: str) -> None:
    """Test updating a ticket."""
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]
    ticket_response = client.post("/api/tickets/", json={"title": "Test Ticket", "description": f"Test Description {test_uuid}", "column_id": column_id})
    ticket_id = ticket_response.json()["id"]

    update_response = client.put(f"/api/tickets/{ticket_id}", json={"title": "Updated Ticket"})
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Ticket"

def test_delete_ticket(client: TestClient, test_uuid: str) -> None:
    """Test deleting a ticket."""
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]
    ticket_response = client.post("/api/tickets/", json={"title": "Test Ticket", "description": f"Test Description {test_uuid}", "column_id": column_id})
    ticket_id = ticket_response.json()["id"]

    delete_response = client.delete(f"/api/tickets/{ticket_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Ticket deleted successfully"