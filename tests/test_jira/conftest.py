import os
import sys
import pytest
from pathlib import Path
from typing import Generator, Dict, Any
from uuid import uuid4
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

# Add the workspace root to the Python path so we can import api modules
workspace_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(workspace_root))

# Import JIRA modules after adding workspace root to path
from api.jira.main import app  # noqa: E402
from api.jira.routes.dependencies.get_session import get_session  # noqa: E402

@pytest.fixture
def test_uuid():
    """Generate a unique UUID for testing."""
    return str(uuid4())

@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """Provide a TestClient for testing with proper mocking."""
    # Set test environment
    os.environ["DATABASE_SCHEMA"] = "test"
    
    # Shared data store across all session instances within the same test
    shared_data: Dict[str, Dict[str, Any]] = {}
    next_ids: Dict[str, int] = {}  # Track next available ID for each model type
    
    # Create a simple mock session that doesn't cause event loop issues
    class MockAsyncSession:
        def __init__(self):
            self.committed = False
            self.closed = False
            self._data = shared_data  # Use shared data store
            self._next_ids = next_ids  # Use shared ID counter
            
        def add(self, item):
            # Simulate adding an item and setting its ID
            model_name = item.__class__.__name__
            
            if hasattr(item, 'id') and item.id is None:
                # Get next available ID for this model type
                if model_name not in self._next_ids:
                    self._next_ids[model_name] = 1
                else:
                    self._next_ids[model_name] += 1
                item.id = self._next_ids[model_name]
            
            # Special handling for Webhook model to ensure event_code is proper EventCode enum
            if model_name == 'Webhook' and hasattr(item, 'event_code'):
                from api.jira.models.events.event_code import EventCode
                if isinstance(item.event_code, str):
                    item.event_code = EventCode(item.event_code)
            
            # Store the item for later retrieval
            if model_name not in self._data:
                self._data[model_name] = {}
            self._data[model_name][item.id] = item
        
        async def commit(self):
            self.committed = True
        
        async def close(self):
            self.closed = True
        
        async def execute(self, stmt):
            # Mock execute for test purposes - return a mock result
            class MockResult:
                def __init__(self, data=None):
                    self.data = data or []
                
                def scalars(self):
                    class MockScalars:
                        def __init__(self, data):
                            self.data = data
                        
                        def all(self):
                            return self.data
                    return MockScalars(self.data)
                
                def scalar_one_or_none(self):
                    if len(self.data) > 0:
                        return self.data[0]
                    return None
            
            # Handle different query types
            try:
                stmt_str = str(stmt)
                
                # Log statement for debugging
                print(f"Mock execute called with: {stmt_str}")
                print(f"Current data store: {self._data}")
                
                # First check for a ticket_comments query
                if ('ticketcomment' in stmt_str.lower() or 'ticket_comment' in stmt_str.lower() or 'TicketComment' in stmt_str) and 'WHERE' in stmt_str:
                    if 'TicketComment' in self._data:
                        comments = list(self._data['TicketComment'].values())
                        print(f"Special case: Returning ticket comments: {comments}")
                        return MockResult(comments)
                
                # Handle general ticket queries
                if ('Ticket' in stmt_str or 'ticket' in stmt_str.lower()) and not ('TicketComment' in stmt_str or 'ticketcomment' in stmt_str.lower()):
                    # Return all tickets in the data store
                    if 'Ticket' in self._data:
                        ticket_values = list(self._data['Ticket'].values())
                        print(f"Returning tickets: {ticket_values}")
                        return MockResult(ticket_values)
                
                elif 'TicketComment' in stmt_str or 'ticketcomment' in stmt_str.lower() or 'ticket_comment' in stmt_str.lower():
                    # Return ticket comments
                    if 'TicketComment' in self._data:
                        comments = list(self._data['TicketComment'].values())
                        print(f"Returning TicketComment objects: {comments}")
                        return MockResult(comments)

                elif 'StatusColumn' in stmt_str or 'status_column' in stmt_str.lower():
                    # Return all columns in the data store
                    if 'StatusColumn' in self._data:
                        column_values = list(self._data['StatusColumn'].values())
                        print(f"Returning columns: {column_values}")
                        return MockResult(column_values)
                
                elif 'Board' in stmt_str or 'board' in stmt_str.lower():
                    # Return all boards in the data store
                    if 'Board' in self._data:
                        # Log what we're returning
                        board_values = list(self._data['Board'].values())
                        print(f"Returning boards: {board_values}")
                        return MockResult(board_values)
                
                # This code is now handled in the earlier conditions
                
                # Handle other table queries 
                elif hasattr(stmt, 'table') and hasattr(stmt.table, 'name'):
                    table_name = stmt.table.name
                    model_name_map = {
                        'board': 'Board',
                        'status_column': 'StatusColumn', 
                        'ticket': 'Ticket',
                        'ticketcomment': 'TicketComment',
                        'webhook': 'Webhook'
                    }
                    
                    if table_name in model_name_map:
                        model_name = model_name_map[table_name]
                        if model_name in self._data:
                            values = list(self._data[model_name].values())
                            print(f"Returning {model_name} values: {values}")
                            return MockResult(values)
                
            except Exception as e:
                print(f"Error in mock execute: {e}")
            
            # Default: return empty result
            return MockResult([])
        
        async def get(self, model_class, obj_id):
            # Mock get method to retrieve objects by ID
            model_name = model_class.__name__
            if model_name in self._data and obj_id in self._data[model_name]:
                return self._data[model_name][obj_id]
            return None
        
        async def delete(self, item):
            # Mock delete method
            if hasattr(item, 'id') and item.id is not None:
                model_name = item.__class__.__name__
                if model_name in self._data and item.id in self._data[model_name]:
                    del self._data[model_name][item.id]
        
        async def refresh(self, item):
            # Mock refresh for test purposes - just ensure the item has an ID
            if hasattr(item, 'id') and item.id is None:
                item.id = 1
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.close()
    
    # Create an async generator that yields our mock session
    async def get_test_session():
        session = MockAsyncSession()
        try:
            yield session
        finally:
            await session.close()
    
    # Override the get_session dependency
    app.dependency_overrides[get_session] = get_test_session
    
    # Mock the WebhookManager to use AsyncMock
    with patch('api.jira.lifespan.WebhookManager') as mock_webhook_manager_class:
        mock_webhook_manager = AsyncMock()
        mock_webhook_manager_class.return_value = mock_webhook_manager
        
        with TestClient(app) as c:
            yield c
            
    # Clean up dependency overrides
    app.dependency_overrides.clear()