"""Health check business logic."""

from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import settings
from .constants import HealthStatus


async def get_health_status() -> dict:
    """
    Check application health status.

    Returns a dictionary containing health status and component checks.
    """
    now = datetime.now(ZoneInfo("UTC")).isoformat()

    checks = {
        "app": "operational",
        "observability": "configured",
    }

    return {
        "status": HealthStatus.HEALTHY,
        "pod_name": settings.POD_NAME,
        "app_version": settings.APP_VERSION,
        "timestamp": now,
        "checks": checks,
    }
