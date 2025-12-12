"""Health check schemas (Pydantic models)."""

from typing import Any, Optional

from app.schemas import CustomModel
from .constants import HealthStatus


class HealthCheckResponse(CustomModel):
    """Health check response model."""

    status: HealthStatus
    pod_name: str
    app_version: str
    timestamp: str
    checks: dict[str, Any] = {}
    details: Optional[dict[str, str]] = None
