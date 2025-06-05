from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    session_maker = request.app.state.session_maker
    session: AsyncSession = session_maker()
    try:
        yield session
    finally:
        await session.close()