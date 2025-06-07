from fastapi import APIRouter
from typing import List
from ...models import StatusColumn
from .create_column import create_column
from .get_columns import get_columns
from .get_column_by_id import get_column_by_id
from .update_column import update_column
from .delete_column import delete_column

router = APIRouter()

router.add_api_route("/", create_column, methods=["POST"], response_model=StatusColumn)
router.add_api_route("/", get_columns, methods=["GET"], response_model=List[StatusColumn])
router.add_api_route("/{column_id}", get_column_by_id, methods=["GET"], response_model=StatusColumn)
router.add_api_route("/{column_id}", update_column, methods=["PUT"], response_model=StatusColumn)
router.add_api_route("/{column_id}", delete_column, methods=["DELETE"], response_model=dict)

__all__ = [
    "router",
    "create_column",
    "get_columns", 
    "get_column_by_id",
    "update_column",
    "delete_column",
]
