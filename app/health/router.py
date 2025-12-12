"""Health check endpoints."""

from fastapi import APIRouter, Depends, status

from .dependencies import valid_health_check
from .schemas import HealthCheckResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    description="Get application health status",
    summary="Health Check",
)
async def get_health(
    health_data: dict = Depends(valid_health_check),
) -> HealthCheckResponse:
    """
    Check if the application is healthy.

    Returns:
        HealthCheckResponse: Current health status with component checks
    """
    return HealthCheckResponse(**health_data)
