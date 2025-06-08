from fastapi.testclient import TestClient
import pytest


def test_get_columns(client, test_uuid):
    """Test reading all columns."""
    # Create a board first
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    
    # Create a column linked to the board
    client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})

    # Test getting all columns
    response = client.get("/api/columns/")
    
    # Verify response
    assert response.status_code == 200
    columns = response.json()
    assert isinstance(columns, list)
    
    # At least our newly created column should be in the list
    assert any(col["name"] == f"Column-{test_uuid}" for col in columns)


def test_get_columns_empty(client):
    """Test getting columns when there are none (or filtered to none)."""
    # Use a random filter that won't match anything
    response = client.get("/api/columns/?name=nonexistent_column_name_xyz")
    
    # Should return an empty list, not an error
    assert response.status_code == 200
    assert response.json() == []
