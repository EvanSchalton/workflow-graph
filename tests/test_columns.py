import pytest

def test_create_column(client, test_uuid):
    """Test creating a column with a valid board."""
    # Create a board first
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column linked to the board
    response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    assert response.status_code == 200
    assert response.json()["name"] == f"Column-{test_uuid}"

def test_read_columns(client, test_uuid):
    """Test reading all columns."""
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})

    response = client.get("/api/columns/")
    assert response.status_code == 200

def test_read_column(client, test_uuid):
    """Test reading a specific column by ID."""
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    response = client.get(f"/api/columns/{column_id}")
    assert response.status_code == 200
    assert response.json()["id"] == column_id

def test_update_column(client, test_uuid):
    """Test updating a column with a valid board."""
    # Create a board first
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column linked to the board
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Update the column
    update_response = client.put(f"/api/columns/{column_id}", json={"name": f"Updated Column-{test_uuid}"})
    assert update_response.status_code == 200
    assert update_response.json()["name"] == f"Updated Column-{test_uuid}"

def test_delete_column(client, test_uuid):
    """Test deleting a column with a valid board."""
    # Create a board first
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column linked to the board
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Delete the column
    delete_response = client.delete(f"/api/columns/{column_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Column deleted successfully"