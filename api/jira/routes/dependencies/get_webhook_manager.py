from fastapi import Request
from ...webhook_manager import WebhookManager

async def get_webhook_manager(request: Request) -> WebhookManager:
    return request.app.state.webhook_manager
