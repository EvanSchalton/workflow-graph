import pytest

def test_create_board(client, test_uuid):
    """Test creating a board."""
    response = client.post("/boards/", json={"name": f"Test Board {test_uuid}"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == f"Test Board {test_uuid}"