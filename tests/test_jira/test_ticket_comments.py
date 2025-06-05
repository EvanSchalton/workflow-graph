import pytest
from api.jira.models import TicketComment

def test_create_comment(client, test_uuid):
    """Test creating a comment on a ticket."""
    # Create a board first
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column linked to the board
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Create a ticket
    ticket_response = client.post("/api/tickets/", json={"title": "Test Ticket", "description": f"Test Description {test_uuid}", "column_id": column_id})
    ticket_id = ticket_response.json()["id"]

    # Create a comment
    response = client.post(f"/api/tickets/{ticket_id}/comments", json={
        "author": "Test Author",
        "message": "Test Comment Message"
    })
    assert response.status_code == 200
    assert response.json()["author"] == "Test Author"
    assert response.json()["message"] == "Test Comment Message"
    assert response.json()["ticket_id"] == ticket_id

def test_read_comments(client, test_uuid):
    """Test reading all comments for a ticket."""
    # Create a board
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Create a ticket
    ticket_response = client.post("/api/tickets/", json={"title": "Test Ticket", "description": f"Test Description {test_uuid}", "column_id": column_id})
    ticket_id = ticket_response.json()["id"]

    # Create two comments
    client.post(f"/api/tickets/{ticket_id}/comments", json={
        "author": "Author 1",
        "message": "Comment 1"
    })
    client.post(f"/api/tickets/{ticket_id}/comments", json={
        "author": "Author 2",
        "message": "Comment 2"
    })

    # Get all comments
    response = client.get(f"/api/tickets/{ticket_id}/comments")
    assert response.status_code == 200
    comments = response.json()
    assert len(comments) == 2
    assert {c["author"] for c in comments} == {"Author 1", "Author 2"}
    assert {c["message"] for c in comments} == {"Comment 1", "Comment 2"}

def test_read_comment(client, test_uuid):
    """Test reading a specific comment by ID."""
    # Create a board
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Create a ticket
    ticket_response = client.post("/api/tickets/", json={"title": "Test Ticket", "description": f"Test Description {test_uuid}", "column_id": column_id})
    ticket_id = ticket_response.json()["id"]

    # Create a comment
    comment_response = client.post(f"/api/tickets/{ticket_id}/comments", json={
        "author": "Test Author",
        "message": "Test Message"
    })
    comment_id = comment_response.json()["id"]

    # Get the specific comment
    response = client.get(f"/api/tickets/{ticket_id}/comments/{comment_id}")
    assert response.status_code == 200
    assert response.json()["id"] == comment_id
    assert response.json()["author"] == "Test Author"
    assert response.json()["message"] == "Test Message"

def test_update_comment(client, test_uuid):
    """Test updating a comment."""
    # Create a board
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Create a ticket
    ticket_response = client.post("/api/tickets/", json={"title": "Test Ticket", "description": f"Test Description {test_uuid}", "column_id": column_id})
    ticket_id = ticket_response.json()["id"]

    # Create a comment
    comment_response = client.post(f"/api/tickets/{ticket_id}/comments", json={
        "author": "Original Author",
        "message": "Original Message"
    })
    comment_id = comment_response.json()["id"]

    # Update the comment
    update_response = client.put(f"/api/tickets/{ticket_id}/comments/{comment_id}", json={
        "author": "Updated Author",
        "message": "Updated Message"
    })
    assert update_response.status_code == 200
    assert update_response.json()["author"] == "Updated Author"
    assert update_response.json()["message"] == "Updated Message"

def test_delete_comment(client, test_uuid):
    """Test deleting a comment."""
    # Create a board
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Create a ticket
    ticket_response = client.post("/api/tickets/", json={"title": "Test Ticket", "description": f"Test Description {test_uuid}", "column_id": column_id})
    ticket_id = ticket_response.json()["id"]

    # Create a comment
    comment_response = client.post(f"/api/tickets/{ticket_id}/comments", json={
        "author": "Test Author",
        "message": "Test Message"
    })
    comment_id = comment_response.json()["id"]

    # Delete the comment
    delete_response = client.delete(f"/api/tickets/{ticket_id}/comments/{comment_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Comment deleted successfully"

    # Verify comment is gone
    get_response = client.get(f"/api/tickets/{ticket_id}/comments/{comment_id}")
    assert get_response.status_code == 404

def test_comment_not_found(client, test_uuid):
    """Test proper handling of non-existent comments."""
    # Create a board
    board_response = client.post("/api/boards/", json={"name": f"Test Board {test_uuid}"})
    board_id = board_response.json()["id"]

    # Create a column
    column_response = client.post("/api/columns/", json={"name": f"Column-{test_uuid}", "board_id": board_id})
    column_id = column_response.json()["id"]

    # Create a ticket
    ticket_response = client.post("/api/tickets/", json={"title": "Test Ticket", "description": f"Test Description {test_uuid}", "column_id": column_id})
    ticket_id = ticket_response.json()["id"]

    non_existent_id = 99999

    # Try to get non-existent comment
    get_response = client.get(f"/api/tickets/{ticket_id}/comments/{non_existent_id}")
    assert get_response.status_code == 404

    # Try to update non-existent comment
    update_response = client.put(f"/api/tickets/{ticket_id}/comments/{non_existent_id}", json={
        "author": "Updated Author",
        "message": "Updated Message"
    })
    assert update_response.status_code == 404

    # Try to delete non-existent comment
    delete_response = client.delete(f"/api/tickets/{ticket_id}/comments/{non_existent_id}")
    assert delete_response.status_code == 404
