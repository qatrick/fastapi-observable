"""Health check specific exceptions."""

from fastapi import HTTPException, status


class HealthCheckFailed(HTTPException):
    """Raised when health check fails."""

    def __init__(self, detail: str = "Health check failed"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        )
