from fastapi import APIRouter
from typing import List
from ...models import Ticket
from .create_ticket import create_ticket
from .get_tickets import get_tickets
from .get_ticket_by_id import get_ticket_by_id
from .update_ticket import update_ticket
from .delete_ticket import delete_ticket

router = APIRouter()

router.add_api_route("/", create_ticket, methods=["POST"], response_model=Ticket)
router.add_api_route("/", get_tickets, methods=["GET"], response_model=List[Ticket])
router.add_api_route("/{ticket_id}", get_ticket_by_id, methods=["GET"], response_model=Ticket)
router.add_api_route("/{ticket_id}", update_ticket, methods=["PUT"], response_model=Ticket)
router.add_api_route("/{ticket_id}", delete_ticket, methods=["DELETE"], response_model=dict)

__all__ = [
    "router",
    "create_ticket",
    "get_tickets", 
    "get_ticket_by_id",
    "update_ticket",
    "delete_ticket",
]
