from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    print("request.app.state", request.app.state)
    print("dir(request.app.state)", dir(request.app.state))
    async_session = request.app.state.async_session
    async with async_session() as session:
        yield session