"""Global application dependencies."""

from typing import Any

from fastapi import Query

from app.exceptions import ValidationError


class PaginationParams:
    """
    Pagination parameters dependency.

    This demonstrates dependency injection best practices:
    - Reusable across multiple routes
    - Cached within request scope
    - Easy to extend and test
    """

    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of items to skip"),
        limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    ):
        self.skip = skip
        self.limit = limit


async def get_pagination_params(
    pagination: PaginationParams = PaginationParams(),
) -> dict[str, Any]:
    """
    Get and validate pagination parameters.

    Dependencies can be chained and will be cached within a request scope,
    meaning this function is called only once per request even if used
    in multiple endpoints.
    """
    return {"skip": pagination.skip, "limit": pagination.limit}
