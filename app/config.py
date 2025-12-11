from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "fastapi-tanzu-app"
    ENV: str = "local"
    ENABLE_METRICS: bool = True
    
    # Observability
    TEMPO_ENDPOINT: str = "http://tempo.monitoring.svc.cluster.local:4317"
    PYROSCOPE_SERVER_ADDRESS: str = "http://pyroscope.monitoring.svc.cluster.local:4040"
    
    # Downward API injected
    POD_NAME: str = "unknown-pod"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()