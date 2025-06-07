from fastapi import APIRouter
from typing import List
from ...models import TicketComment
from .create_comment import create_comment
from .read_comments import read_comments
from .read_comment import read_comment
from .update_comment import update_comment
from .delete_comment import delete_comment

router = APIRouter()

router.add_api_route("/{ticket_id}/comments", create_comment, methods=["POST"], response_model=TicketComment)
router.add_api_route("/{ticket_id}/comments", read_comments, methods=["GET"], response_model=List[TicketComment])
router.add_api_route("/{ticket_id}/comments/{comment_id}", read_comment, methods=["GET"], response_model=TicketComment)
router.add_api_route("/{ticket_id}/comments/{comment_id}", update_comment, methods=["PUT"], response_model=TicketComment)
router.add_api_route("/{ticket_id}/comments/{comment_id}", delete_comment, methods=["DELETE"], response_model=dict)

__all__ = [
    "router",
    "create_comment",
    "read_comments",
    "read_comment",
    "update_comment", 
    "delete_comment",
]
