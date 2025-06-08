from fastapi.testclient import TestClient
import pytest


def test_get_boards(client, test_uuid):
    """Test retrieving all boards."""
    # Create some test boards first
    board1 = client.post("/api/boards/", json={"name": f"Test Board 1 {test_uuid}"})
    board2 = client.post("/api/boards/", json={"name": f"Test Board 2 {test_uuid}"})
    
    # Get all boards
    response = client.get("/api/boards/")
    assert response.status_code == 200
    
    # Check response is a list
    boards = response.json()
    assert isinstance(boards, list)
    
    # Verify our created boards are in the response
    board_ids = {board1.json()["id"], board2.json()["id"]}
    found_boards = [board for board in boards if board["id"] in board_ids]
    
    assert len(found_boards) == 2
    
    # Verify board contents
    for board in found_boards:
        if board["name"] == f"Test Board 1 {test_uuid}":
            assert board["id"] == board1.json()["id"]
        elif board["name"] == f"Test Board 2 {test_uuid}":
            assert board["id"] == board2.json()["id"]
