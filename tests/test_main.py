import pytest

def test_create_board(client, test_uuid):
    """Test creating a board."""
    response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == f"Test Board {test_uuid}"

def test_create_column(client, test_uuid):
    """Test creating a column with a valid board."""
    # Create a board first
    board_response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column linked to the board
    response = client.post("/columns/", json={"name": "Test Column", "board_id": board_id})
    assert response.status_code == 200
    assert response.json()["name"] == "Test Column"

def test_create_ticket(client, test_uuid):
    """Test creating a ticket with a valid column."""
    # Create a board first
    board_response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column linked to the board
    column_response = client.post("/columns/", json={"name": "Test Column", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Create a ticket linked to the column
    response = client.post("/tickets/", json={"title": "Test Ticket", "description": "Test Description", "column_id": column_id})
    assert response.status_code == 200
    assert response.json()["title"] == "Test Ticket"

def test_update_column(client, test_uuid):
    """Test updating a column with a valid board."""
    # Create a board first
    board_response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column linked to the board
    column_response = client.post("/columns/", json={"name": "Test Column", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Update the column
    update_response = client.put(f"/columns/{column_id}", json={"name": "Updated Column"})
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Column"

def test_delete_column(client, test_uuid):
    """Test deleting a column with a valid board."""
    # Create a board first
    board_response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column linked to the board
    column_response = client.post("/columns/", json={"name": "Test Column", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Delete the column
    delete_response = client.delete(f"/columns/{column_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Column deleted successfully"

def test_read_boards(client):
    """Test reading all boards."""
    response = client.get("/boards/")
    assert response.status_code == 200

def test_read_board(client, test_uuid):
    """Test reading a specific board by ID."""
    board_response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    response = client.get(f"/boards/{board_id}")
    assert response.status_code == 200
    assert response.json()["id"] == board_id

def test_read_columns(client, test_uuid):
    """Test reading all columns."""
    board_response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    client.post("/columns/", json={"name": "Test Column", "board_id": board_id})

    response = client.get("/columns/")
    assert response.status_code == 200

def test_read_column(client, test_uuid):
    """Test reading a specific column by ID."""
    board_response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    column_response = client.post("/columns/", json={"name": "Test Column", "board_id": board_id})
    column_id = column_response.json()["id"]

    response = client.get(f"/columns/{column_id}")
    assert response.status_code == 200
    assert response.json()["id"] == column_id

def test_read_tickets(client, test_uuid):
    """Test reading all tickets."""
    board_response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    column_response = client.post("/columns/", json={"name": "Test Column", "board_id": board_id})
    column_id = column_response.json()["id"]
    client.post("/tickets/", json={"title": "Test Ticket", "description": "Test Description", "column_id": column_id})

    response = client.get("/tickets/")
    assert response.status_code == 200

def test_read_ticket(client, test_uuid):
    """Test reading a specific ticket by ID."""
    board_response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    column_response = client.post("/columns/", json={"name": "Test Column", "board_id": board_id})
    column_id = column_response.json()["id"]
    ticket_response = client.post("/tickets/", json={"title": "Test Ticket", "description": "Test Description", "column_id": column_id})
    ticket_id = ticket_response.json()["id"]

    response = client.get(f"/tickets/{ticket_id}")
    assert response.status_code == 200
    assert response.json()["id"] == ticket_id

def test_update_ticket(client, test_uuid):
    """Test updating a ticket."""
    board_response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    column_response = client.post("/columns/", json={"name": "Test Column", "board_id": board_id})
    column_id = column_response.json()["id"]
    ticket_response = client.post("/tickets/", json={"title": "Test Ticket", "description": "Test Description", "column_id": column_id})
    ticket_id = ticket_response.json()["id"]

    update_response = client.put(f"/tickets/{ticket_id}", json={"title": "Updated Ticket"})
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Ticket"

def test_delete_ticket(client, test_uuid):
    """Test deleting a ticket."""
    board_response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    column_response = client.post("/columns/", json={"name": "Test Column", "board_id": board_id})
    column_id = column_response.json()["id"]
    ticket_response = client.post("/tickets/", json={"title": "Test Ticket", "description": "Test Description", "column_id": column_id})
    ticket_id = ticket_response.json()["id"]

    delete_response = client.delete(f"/tickets/{ticket_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Ticket deleted successfully"

def test_create_webhook(client, test_uuid):
    """Test creating a webhook."""
    response = client.post("/webhooks/", json={"url": "http://example.com/webhook", "event": test_uuid})
    assert response.status_code == 200
    assert response.json()["url"] == "http://example.com/webhook"
    assert response.json()["event"] == test_uuid

def test_read_webhooks(client, test_uuid):
    """Test reading all webhooks."""
    client.post("/webhooks/", json={"url": "http://example.com/webhook", "event": test_uuid})

    response = client.get("/webhooks/")
    assert response.status_code == 200

def test_read_webhook(client, test_uuid):
    """Test reading a specific webhook by ID."""
    webhook_response = client.post("/webhooks/", json={"url": "http://example.com/webhook", "event": test_uuid})
    webhook_id = webhook_response.json()["id"]

    response = client.get(f"/webhooks/{webhook_id}")
    assert response.status_code == 200
    assert response.json()["id"] == webhook_id
    assert response.json()["event"] == test_uuid

def test_update_webhook(client, test_uuid):
    """Test updating a webhook."""
    webhook_response = client.post("/webhooks/", json={"url": "http://example.com/webhook", "event": test_uuid})
    webhook_id = webhook_response.json()["id"]

    update_response = client.put(f"/webhooks/{webhook_id}", json={"url": "http://example.com/updated-webhook", "event": test_uuid})
    assert update_response.status_code == 200
    assert update_response.json()["url"] == "http://example.com/updated-webhook"
    assert update_response.json()["event"] == test_uuid

def test_delete_webhook(client, test_uuid):
    """Test deleting a webhook."""
    webhook_response = client.post("/webhooks/", json={"url": "http://example.com/webhook", "event": test_uuid})
    webhook_id = webhook_response.json()["id"]

    delete_response = client.delete(f"/webhooks/{webhook_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Webhook deleted successfully"