"""Health check dependencies."""

from .service import get_health_status


async def valid_health_check() -> dict:
    """Validate that application is healthy."""
    health = await get_health_status()
    return health
