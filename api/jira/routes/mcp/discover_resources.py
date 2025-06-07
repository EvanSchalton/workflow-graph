from typing import Dict, Any


async def discover_resources() -> Dict[str, Any]:
    """Discover available MCP resources."""
    return {
        "boards": {
            "url": "/mcp/resources/boards",
            "methods": {
                "GET": "Retrieve all boards",
                "POST": {
                    "description": "Create a new board",
                    "payload": {
                        "name": "string"
                    }
                },
                "GET /{board_id}": "Retrieve a specific board by ID"
            }
        },
        "tickets": {
            "url": "/mcp/resources/tickets",
            "methods": {
                "GET": "Retrieve all tickets",
                "POST": {
                    "description": "Create a new ticket",
                    "payload": {
                        "title": "string",
                        "description": "string (optional)",
                        "assignee": "string (optional)",
                        "conversation": "string (optional)",
                        "column_id": "integer"
                    }
                },
                "GET /{ticket_id}": "Retrieve a specific ticket by ID"
            }
        },
        "columns": {
            "url": "/mcp/resources/columns",
            "methods": {
                "GET": "Retrieve all columns",
                "POST": {
                    "description": "Create a new column",
                    "payload": {
                        "name": "string",
                        "board_id": "integer"
                    }
                },
                "GET /{column_id}": "Retrieve a specific column by ID"
            }
        }
    }
