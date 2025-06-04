from fastapi import Request
from sqlalchemy.orm import Session

async def get_session(request: Request) -> Session:
    print("request.app.state", request.app.state)
    print("dir(request.app.state)", dir(request.app.state))
    return request.app.state.session