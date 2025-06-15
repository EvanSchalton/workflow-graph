# filepath: tests/test_api/test_jira/test_routes/test_boards/boards_test.py
"""
COMPLETE MIGRATION: boards_test.py
Source: tests/test_jira/boards_test.py
Migrated: 2025-06-15 19:35:42
Test Functions: 4
Status: COMPLETE - All content migrated
"""


# MIGRATED: Content moved to tests/test_api/test_jira/test_routes/test_boards/ (multiple files)
# This file is kept for reference but all tests have been migrated to the new structure
# Date: 2025-06-15
# Migration completed: 4 test functions migrated successfully to separate files

from fastapi.testclient import TestClient
import pytest


def test_create_board(client, test_uuid):
    """Test creating a board."""
    response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == f"Test Board {test_uuid}"

def test_read_boards(client):
    """Test reading all boards."""
    response = client.get("/api/boards/")
    assert response.status_code == 200

def test_read_board(client, test_uuid):
    """Test reading a specific board by ID."""
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    response = client.get(f"/api/boards/{board_id}")
    assert response.status_code == 200
    assert response.json()["id"] == board_id

def test_delete_board(client, test_uuid):
    """Test deleting a board."""
    # Create a board first
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Delete the board
    delete_response = client.delete(f"/api/boards/{board_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Board deleted successfully"