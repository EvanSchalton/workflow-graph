from typing import Dict, Any


async def discover_tools() -> Dict[str, Any]:
    """Discover available MCP tools."""
    return {
        "create_board": {
            "url": "/mcp/resources/boards",
            "method": "POST",
            "payload": {
                "name": "string"
            }
        },
        "update_board": {
            "url": "/mcp/resources/boards/{board_id}",
            "method": "PUT",
            "payload": {
                "name": "string (optional)"
            }
        },
        "delete_board": {
            "url": "/mcp/resources/boards/{board_id}",
            "method": "DELETE"
        },
        "create_ticket": {
            "url": "/mcp/resources/tickets",
            "method": "POST",
            "payload": {
                "title": "string",
                "description": "string (optional)",
                "assignee": "string (optional)",
                "conversation": "string (optional)",
                "column_id": "integer"
            }
        },
        "update_ticket": {
            "url": "/mcp/resources/tickets/{ticket_id}",
            "method": "PUT",
            "payload": {
                "title": "string (optional)",
                "description": "string (optional)",
                "assignee": "string (optional)",
                "conversation": "string (optional)",
                "column_id": "integer (optional)"
            }
        },
        "delete_ticket": {
            "url": "/mcp/resources/tickets/{ticket_id}",
            "method": "DELETE"
        },
        "create_column": {
            "url": "/mcp/resources/columns",
            "method": "POST",
            "payload": {
                "name": "string",
                "board_id": "integer"
            }
        },
        "update_column": {
            "url": "/mcp/resources/columns/{column_id}",
            "method": "PUT",
            "payload": {
                "name": "string (optional)",
                "board_id": "integer (optional)"
            }
        },
        "delete_column": {
            "url": "/mcp/resources/columns/{column_id}",
            "method": "DELETE"
        }
    }
