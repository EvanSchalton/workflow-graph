from fastapi.testclient import TestClient
import pytest


def test_create_column(client, test_uuid):
    """Test creating a new column for a board."""
    # Create a board first
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    
    # Create a column linked to the board
    column_data = {"name": f"Test Column {test_uuid}", "board_id": board_id}
    response = client.post("/api/columns/", json=column_data)
    
    # Verify response
    assert response.status_code == 200
    column = response.json()
    assert column["name"] == f"Test Column {test_uuid}"
    assert column["board_id"] == board_id
    assert "id" in column
    
    # Verify the column was actually created by retrieving it
    get_response = client.get(f"/api/columns/{column['id']}")
    assert get_response.status_code == 200
    retrieved_column = get_response.json()
    assert retrieved_column["id"] == column["id"]
    assert retrieved_column["name"] == column["name"]
    assert retrieved_column["board_id"] == board_id


def test_create_column_invalid_board(client, test_uuid):
    """Test creating a column with an invalid board ID."""
    # Use a board ID that is unlikely to exist
    invalid_board_id = 99999
    column_data = {"name": f"Invalid Board Column {test_uuid}", "board_id": invalid_board_id}
    
    response = client.post("/api/columns/", json=column_data)
    
    # The API should return an error
    assert response.status_code in (400, 404, 422)  # Depends on how the API handles invalid foreign keys
