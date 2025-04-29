from typing import Generator, AsyncGenerator
import asyncio
import pytest
from uuid import uuid4
from pathlib import Path
import sys
from fastapi.testclient import TestClient
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from unittest.mock import patch
import os

sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.jira.main import app, DATABASE_URL

@pytest.fixture
def test_uuid():
    """Generate a unique UUID for testing."""
    return str(uuid4())

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Provide a TestClient for testing, ensuring the app's lifespan is started and tied to the test_db."""
    os.environ["DATABASE_SCHEMA"] = "test"

    with TestClient(app) as c:
        # Manually start the app's lifespan
        asyncio.run(app.router.startup())
        try:
            yield c
        finally:
            # Manually stop the app's lifespan
            asyncio.run(app.router.shutdown())

@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Override the database handler to use the 'test' schema."""
    engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)

    # Create the test schema
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = sessionmaker( # type: ignore
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    yield async_session()

    # Drop the test schema after the test
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()