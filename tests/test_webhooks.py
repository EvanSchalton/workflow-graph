import pytest

def test_create_webhook(client, test_uuid):
    """Test creating a webhook."""
    response = client.post("/api/webhooks/", json={"url": "http://example.com/webhook", "event": test_uuid})
    assert response.status_code == 200
    assert response.json()["url"] == "http://example.com/webhook"
    assert response.json()["event"] == test_uuid

def test_read_webhooks(client, test_uuid):
    """Test reading all webhooks."""
    client.post("/api/webhooks/", json={"url": "http://example.com/webhook", "event": test_uuid})

    response = client.get("/api/webhooks/")
    assert response.status_code == 200

def test_read_webhook(client, test_uuid):
    """Test reading a specific webhook by ID."""
    webhook_response = client.post("/api/webhooks/", json={"url": "http://example.com/webhook", "event": test_uuid})
    webhook_id = webhook_response.json()["id"]

    response = client.get(f"/api/webhooks/{webhook_id}")
    assert response.status_code == 200
    assert response.json()["id"] == webhook_id
    assert response.json()["event"] == test_uuid

def test_update_webhook(client, test_uuid):
    """Test updating a webhook."""
    webhook_response = client.post("/api/webhooks/", json={"url": "http://example.com/webhook", "event": test_uuid})
    webhook_id = webhook_response.json()["id"]

    update_response = client.put(f"/api/webhooks/{webhook_id}", json={"url": "http://example.com/updated-webhook", "event": test_uuid})
    assert update_response.status_code == 200
    assert update_response.json()["url"] == "http://example.com/updated-webhook"
    assert update_response.json()["event"] == test_uuid

def test_delete_webhook(client, test_uuid):
    """Test deleting a webhook."""
    webhook_response = client.post("/api/webhooks/", json={"url": "http://example.com/webhook", "event": test_uuid})
    webhook_id = webhook_response.json()["id"]

    delete_response = client.delete(f"/api/webhooks/{webhook_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Webhook deleted successfully"