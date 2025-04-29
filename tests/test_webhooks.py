import pytest
from random import choice
from app.jira.models.webhook.webhook_event_code import WebhookEventCode
from fastapi.testclient import TestClient

@pytest.fixture
def event_code() -> WebhookEventCode:
    return choice(list(WebhookEventCode))

@pytest.fixture
def url(test_uuid: str) -> str:
    """Generate a random URL for the webhook."""
    return f"http://example.com/webhook/{test_uuid}"

def test_create_webhook(client: TestClient, url: str, event_code:WebhookEventCode):
    """Test creating a webhook."""
    response = client.post("/api/webhooks/", json={"url": url, "event_code": event_code.value})
    assert response.status_code == 200
    assert response.json()["url"] == url
    assert response.json()["event_code"] == event_code.value

def test_read_webhooks(client: TestClient, url: str, event_code:WebhookEventCode):
    """Test reading all webhooks."""
    client.post("/api/webhooks/", json={"url": url, "event_code": event_code.value})

    response = client.get("/api/webhooks/")
    assert response.status_code == 200

def test_read_webhook(client: TestClient, url: str, event_code:WebhookEventCode):
    """Test reading a specific webhook by ID."""
    webhook_response = client.post("/api/webhooks/", json={"url": url, "event_code": event_code.value})
    webhook_id = webhook_response.json()["id"]

    response = client.get(f"/api/webhooks/{webhook_id}")
    assert response.status_code == 200
    assert response.json()["id"] == webhook_id
    assert response.json()["event_code"] == event_code.value

def test_update_webhook(client: TestClient, url: str, event_code:WebhookEventCode):
    """Test updating a webhook."""
    update_url = f"{url}/updated"
    webhook_response = client.post("/api/webhooks/", json={"url": url, "event_code": event_code.value})
    webhook_id = webhook_response.json()["id"]

    update_response = client.put(f"/api/webhooks/{webhook_id}", json={"url": update_url, "event_code": event_code.value})
    assert update_response.status_code == 200
    assert update_response.json()["url"] == update_url
    assert update_response.json()["event_code"] == event_code.value

def test_delete_webhook(client: TestClient, url: str, event_code:WebhookEventCode):
    """Test deleting a webhook."""
    webhook_response = client.post("/api/webhooks/", json={"url": url, "event_code": event_code.value})
    webhook_id = webhook_response.json()["id"]

    delete_response = client.delete(f"/api/webhooks/{webhook_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Webhook deleted successfully"