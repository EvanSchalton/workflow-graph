from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.sql import text
from sqlmodel import SQLModel
import os
from .webhook_manager import WebhookManager
from .websocket import WebsocketManager

DATABASE_URL = "postgresql+asyncpg://jira:jira@docker.lan:5432/postgres"

# Define lifespan event handlers
@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    print("Starting lifespan...")
    
    database_url = os.getenv("DATABASE_URL", DATABASE_URL)
    schema = os.getenv("DATABASE_SCHEMA", "public")
    engine = create_async_engine(database_url, echo=True)

    # Create session maker for async sessions
    session_maker = async_sessionmaker(
        bind=engine,
        expire_on_commit=False
    )
    session: AsyncSession = session_maker()

    # Create tables in the specified schema
    async with engine.begin() as conn:
        await conn.execute(text(f"SET search_path TO {schema}"))
        await conn.run_sync(SQLModel.metadata.create_all)

    app.state.engine = engine
    app.state.session_maker = session_maker
    app.state.session = session
    app.state.webhook_manager = WebhookManager(session=session)
    print("Creating WebsocketManager...")
    app.state.websocket_manager = WebsocketManager()
    print("WebsocketManager created.", id(app.state.websocket_manager))

    print("lifespan app.state.engine:", app.state.engine)
    print("lifespan app.state.session:", app.state.session)
    print("lifespan app.state.webhook_manager:", app.state.webhook_manager)
    print("lifespan app.state.websocket_manager:", app.state.websocket_manager)

    try:
        yield
    finally:
        print("Stopping lifespan...")
        await engine.dispose()
