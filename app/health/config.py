"""Health check module configuration."""

from pydantic_settings import BaseSettings


class HealthConfig(BaseSettings):
    """Health check specific configuration."""

    HEALTH_CHECK_TIMEOUT: int = 5  # seconds


health_settings = HealthConfig()
