from fastapi.testclient import TestClient
import pytest


def test_update_column(client, test_uuid):
    """Test updating a column."""
    # Create a board first
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    
    # Create a column linked to the board
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Update the column
    updated_name = f"Updated Column-{test_uuid}"
    response = client.put(f"/api/columns/{column_id}", json={"name": updated_name, "board_id": board_id})
    
    # Verify response
    assert response.status_code == 200
    updated_column = response.json()
    assert updated_column["id"] == column_id
    assert updated_column["name"] == updated_name
    assert updated_column["board_id"] == board_id
    
    # Verify the column was actually updated by retrieving it
    get_response = client.get(f"/api/columns/{column_id}")
    assert get_response.status_code == 200
    retrieved_column = get_response.json()
    assert retrieved_column["name"] == updated_name


def test_update_nonexistent_column(client, test_uuid):
    """Test updating a column that doesn't exist."""
    # Use an ID that shouldn't exist
    nonexistent_id = 99999
    response = client.put(
        f"/api/columns/{nonexistent_id}", 
        json={"name": f"Nonexistent Column-{test_uuid}", "board_id": 1}
    )
    
    # Should return a 404 error
    assert response.status_code == 404
