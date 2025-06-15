"""Tests for api/jira/routes/boards/delete_board_with_events module."""

import pytest
from fastapi.testclient import TestClient


def test_delete_board(client, test_uuid):
    """Test deleting a board."""
    # Create a board first
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Delete the board
    delete_response = client.delete(f"/api/boards/{board_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Board deleted successfully"
