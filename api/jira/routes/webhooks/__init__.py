from fastapi import APIRouter
from typing import List
from ...models.webhook import Webhook
from .create_webhook import create_webhook
from .read_webhooks import read_webhooks
from .read_webhook import read_webhook
from .update_webhook import update_webhook
from .delete_webhook import delete_webhook

router = APIRouter()

router.add_api_route("/", create_webhook, methods=["POST"], response_model=Webhook)
router.add_api_route("/", read_webhooks, methods=["GET"], response_model=List[Webhook])
router.add_api_route("/{webhook_id}", read_webhook, methods=["GET"], response_model=Webhook)
router.add_api_route("/{webhook_id}", update_webhook, methods=["PUT"], response_model=Webhook)
router.add_api_route("/{webhook_id}", delete_webhook, methods=["DELETE"], response_model=dict)

__all__ = [
    "router",
    "create_webhook",
    "read_webhooks",
    "read_webhook",
    "update_webhook",
    "delete_webhook", 
]
