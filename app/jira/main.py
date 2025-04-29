from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.jira.models import SQLModel
from typing import AsyncGenerator, Literal
from .models import Board, StatusColumn, Ticket, Webhook
from typing import List
from sqlalchemy.sql import select, text
import os

DATABASE_URL = "postgresql+asyncpg://jira:jira@docker.lan:5432/postgres"

# Define lifespan event handlers
@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    database_url = os.getenv("DATABASE_URL", DATABASE_URL)
    schema = os.getenv("DATABASE_SCHEMA", "public")
    engine = create_async_engine(database_url, echo=True)

    # Fix sessionmaker arguments
    async_session = sessionmaker( # type: ignore
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # Create tables in the specified schema
    async with engine.begin() as conn:
        await conn.execute(text(f"SET search_path TO {schema}"))
        await conn.run_sync(SQLModel.metadata.create_all)

    app.state.engine = engine
    app.state.async_session = async_session
    try:
        yield
    finally:
        await engine.dispose()

# Initialize FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Dependency to get the database session
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if not hasattr(app.state, "async_session"):
        raise RuntimeError("Application is not fully initialized. Ensure the lifespan handler has run.")

    async_session = app.state.async_session
    async with async_session() as session:
        yield session

# CRUD for Boards
@app.post("/boards/", response_model=Board)
async def create_board(board: Board, session: AsyncSession = Depends(get_session)):
    session.add(board)
    await session.commit()
    await session.refresh(board)
    return board

@app.get("/boards/", response_model=List[Board])
async def read_boards(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Board))
    return result.scalars().all()

@app.get("/boards/{board_id}", response_model=Board)
async def read_board(board_id: int, session: AsyncSession = Depends(get_session)):
    board = await session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@app.put("/boards/{board_id}", response_model=Board)
async def update_board(board_id: int, board: Board, session: AsyncSession = Depends(get_session)):
    existing_board = await session.get(Board, board_id)
    if not existing_board:
        raise HTTPException(status_code=404, detail="Board not found")
    for key, value in board.dict(exclude_unset=True).items():
        setattr(existing_board, key, value)
    session.add(existing_board)
    await session.commit()
    await session.refresh(existing_board)
    return existing_board

@app.delete("/boards/{board_id}", response_model=dict)
async def delete_board(board_id: int, session: AsyncSession = Depends(get_session)):
    board = await session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    await session.delete(board)
    await session.commit()
    return {"message": "Board deleted successfully"}

# CRUD for Columns
@app.post("/columns/", response_model=StatusColumn)
async def create_column(column: StatusColumn, session: AsyncSession = Depends(get_session)):
    session.add(column)
    await session.commit()
    await session.refresh(column)
    return column

@app.get("/columns/", response_model=List[StatusColumn])
async def read_columns(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(StatusColumn))
    return result.scalars().all()

@app.get("/columns/{column_id}", response_model=StatusColumn)
async def read_column(column_id: int, session: AsyncSession = Depends(get_session)):
    column = await session.get(StatusColumn, column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    return column

@app.put("/columns/{column_id}", response_model=StatusColumn)
async def update_column(column_id: int, column: StatusColumn, session: AsyncSession = Depends(get_session)):
    existing_column = await session.get(StatusColumn, column_id)
    if not existing_column:
        raise HTTPException(status_code=404, detail="Column not found")
    for key, value in column.dict(exclude_unset=True).items():
        setattr(existing_column, key, value)
    session.add(existing_column)
    await session.commit()
    await session.refresh(existing_column)
    return existing_column

@app.delete("/columns/{column_id}", response_model=dict)
async def delete_column(column_id: int, session: AsyncSession = Depends(get_session)):
    column = await session.get(StatusColumn, column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    await session.delete(column)
    await session.commit()
    return {"message": "Column deleted successfully"}

# CRUD for Tickets
@app.post("/tickets/", response_model=Ticket)
async def create_ticket(ticket: Ticket, session: AsyncSession = Depends(get_session)):
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    return ticket

@app.get("/tickets/", response_model=List[Ticket])
async def read_tickets(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Ticket))
    return result.scalars().all()

@app.get("/tickets/{ticket_id}", response_model=Ticket)
async def read_ticket(ticket_id: int, session: AsyncSession = Depends(get_session)):
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.put("/tickets/{ticket_id}", response_model=Ticket)
async def update_ticket(ticket_id: int, ticket: Ticket, session: AsyncSession = Depends(get_session)):
    existing_ticket = await session.get(Ticket, ticket_id)
    if not existing_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    for key, value in ticket.dict(exclude_unset=True).items():
        setattr(existing_ticket, key, value)
    session.add(existing_ticket)
    await session.commit()
    await session.refresh(existing_ticket)
    return existing_ticket

@app.delete("/tickets/{ticket_id}", response_model=dict)
async def delete_ticket(ticket_id: int, session: AsyncSession = Depends(get_session)):
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    await session.delete(ticket)
    await session.commit()
    return {"message": "Ticket deleted successfully"}

# CRUD for Webhooks
@app.post("/webhooks/", response_model=Webhook)
async def create_webhook(webhook: Webhook, session: AsyncSession = Depends(get_session)):
    session.add(webhook)
    await session.commit()
    await session.refresh(webhook)
    return webhook

@app.get("/webhooks/", response_model=List[Webhook])
async def read_webhooks(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Webhook))
    return result.scalars().all()

@app.get("/webhooks/{webhook_id}", response_model=Webhook)
async def read_webhook(webhook_id: int, session: AsyncSession = Depends(get_session)):
    webhook = await session.get(Webhook, webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return webhook

@app.put("/webhooks/{webhook_id}", response_model=Webhook)
async def update_webhook(webhook_id: int, webhook: Webhook, session: AsyncSession = Depends(get_session)):
    existing_webhook = await session.get(Webhook, webhook_id)
    if not existing_webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    for key, value in webhook.dict(exclude_unset=True).items():
        setattr(existing_webhook, key, value)
    session.add(existing_webhook)
    await session.commit()
    await session.refresh(existing_webhook)
    return existing_webhook

@app.delete("/webhooks/{webhook_id}", response_model=dict)
async def delete_webhook(webhook_id: int, session: AsyncSession = Depends(get_session)):
    webhook = await session.get(Webhook, webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    await session.delete(webhook)
    await session.commit()
    return {"message": "Webhook deleted successfully"}

@app.get("/")
def read_root():
    return {"message": "Welcome to the lightweight Jira API!"}