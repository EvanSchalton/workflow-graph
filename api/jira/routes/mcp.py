from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from typing import List
from .dependencies import get_session
from ..models.board import Board
from ..models.ticket import Ticket
from ..models.status_column import StatusColumn

router = APIRouter()

@router.get("/resources/boards", response_model=List[Board])
async def get_boards(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Board))
    return result.scalars().all()

@router.get("/resources/boards/{board_id}", response_model=Board)
async def get_board_by_id(board_id: int, session: AsyncSession = Depends(get_session)):
    board = await session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@router.put("/resources/boards/{board_id}", response_model=Board)
async def update_board(board_id: int, board: Board, session: AsyncSession = Depends(get_session)):
    existing_board = await session.get(Board, board_id)
    if not existing_board:
        raise HTTPException(status_code=404, detail="Board not found")
    for key, value in board.model_dump(exclude_unset=True).items():
        setattr(existing_board, key, value)
    session.add(existing_board)
    await session.commit()
    await session.refresh(existing_board)
    return existing_board

@router.delete("/resources/boards/{board_id}", response_model=dict)
async def delete_board(board_id: int, session: AsyncSession = Depends(get_session)):
    board = await session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    await session.delete(board)
    await session.commit()
    return {"message": "Board deleted successfully"}

@router.get("/resources/tickets", response_model=List[Ticket])
async def get_tickets(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Ticket))
    return result.scalars().all()

@router.get("/resources/tickets/{ticket_id}", response_model=Ticket)
async def get_ticket_by_id(ticket_id: int, session: AsyncSession = Depends(get_session)):
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.put("/resources/tickets/{ticket_id}", response_model=Ticket)
async def update_ticket(ticket_id: int, ticket: Ticket, session: AsyncSession = Depends(get_session)):
    existing_ticket = await session.get(Ticket, ticket_id)
    if not existing_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    for key, value in ticket.model_dump(exclude_unset=True).items():
        setattr(existing_ticket, key, value)
    session.add(existing_ticket)
    await session.commit()
    await session.refresh(existing_ticket)
    return existing_ticket

@router.delete("/resources/tickets/{ticket_id}", response_model=dict)
async def delete_ticket(ticket_id: int, session: AsyncSession = Depends(get_session)):
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    await session.delete(ticket)
    await session.commit()
    return {"message": "Ticket deleted successfully"}

@router.get("/resources/columns", response_model=List[StatusColumn])
async def get_columns(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(StatusColumn))
    return result.scalars().all()

@router.get("/resources/columns/{column_id}", response_model=StatusColumn)
async def get_column_by_id(column_id: int, session: AsyncSession = Depends(get_session)):
    column = await session.get(StatusColumn, column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    return column

@router.put("/resources/columns/{column_id}", response_model=StatusColumn)
async def update_column(column_id: int, column: StatusColumn, session: AsyncSession = Depends(get_session)):
    existing_column = await session.get(StatusColumn, column_id)
    if not existing_column:
        raise HTTPException(status_code=404, detail="Column not found")
    for key, value in column.model_dump(exclude_unset=True).items():
        setattr(existing_column, key, value)
    session.add(existing_column)
    await session.commit()
    await session.refresh(existing_column)
    return existing_column

@router.delete("/resources/columns/{column_id}", response_model=dict)
async def delete_column(column_id: int, session: AsyncSession = Depends(get_session)):
    column = await session.get(StatusColumn, column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    await session.delete(column)
    await session.commit()
    return {"message": "Column deleted successfully"}

@router.get("/resources", response_model=dict)
async def discover_resources():
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

@router.get("/tools", response_model=dict)
async def discover_tools():
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