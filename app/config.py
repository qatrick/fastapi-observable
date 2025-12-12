from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application configuration."""

    # App Configuration
    APP_NAME: str = "fastapi-observable"
    APP_VERSION: str = "0.1.0"
    ENV: str = "local"

    # Feature Flags
    ENABLE_METRICS: bool = True

    # Observability
    TEMPO_ENDPOINT: str = "http://tempo.monitoring.svc.cluster.local:4317"
    PYROSCOPE_SERVER_ADDRESS: str = "http://pyroscope.monitoring.svc.cluster.local:4040"

    # Kubernetes - Downward API injected
    POD_NAME: str = "unknown-pod"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()