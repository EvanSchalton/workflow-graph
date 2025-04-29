from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import List
from sqlalchemy.sql import text
from sqlmodel import SQLModel
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
