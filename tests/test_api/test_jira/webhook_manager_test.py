"""Tests for api/jira/webhook_manager module."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from api.jira.webhook_manager import WebhookManager
from api.jira.models import EventCode, Board, BoardEvent, Webhook


@pytest.fixture
def mock_session():
    """Create a mock SQLAlchemy session."""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def webhook_manager(mock_session):
    """Create a WebhookManager instance with a mock session."""
    return WebhookManager(session=mock_session)


@pytest.mark.asyncio
async def test_get_subscribers(webhook_manager, mock_session):
    """Test retrieving webhook subscribers for an event code."""
    # Setup mock webhooks
    mock_webhooks = [MagicMock(), MagicMock()]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_webhooks
    mock_session.execute.return_value = mock_result
    
    # Call the method
    event_code = EventCode.BOARD_CREATE
    subscribers = await webhook_manager.get_subscribers(event_code)
    
    # Verify result
    assert subscribers == mock_webhooks
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_broadcast(webhook_manager, mock_session):
    """Test broadcasting an event to subscribers."""
    # Setup mock webhooks with publish method
    mock_webhook1 = AsyncMock()
    mock_webhook2 = AsyncMock()
    mock_webhooks = [mock_webhook1, mock_webhook2]
    
    # Mock the get_subscribers method to return our mock webhooks
    webhook_manager.get_subscribers = AsyncMock(return_value=mock_webhooks)
    
    # Create a mock event
    mock_board = MagicMock(spec=Board)
