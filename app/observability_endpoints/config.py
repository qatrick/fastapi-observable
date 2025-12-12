"""Observability endpoints configuration."""

from pydantic_settings import BaseSettings


class ObservabilityConfig(BaseSettings):
    """Observability endpoints specific configuration."""

    COMPUTATION_TIMEOUT: int = 30  # seconds
    ENABLE_HEAVY_ENDPOINTS: bool = True


observability_settings = ObservabilityConfig()
