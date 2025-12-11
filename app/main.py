from fastapi import FastAPI
from contextlib import asynccontextmanager
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import make_asgi_app
import logging

from .config import settings
from .logger import setup_logging
from .observability import setup_tracing, setup_profiling

# 1. Setup Logger immediately
setup_logging(settings.APP_NAME, settings.ENV)
logger = logging.getLogger("app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} in {settings.ENV}")
    setup_tracing()
    setup_profiling()
    yield
    logger.info("Shutting down")

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# 2. Metrics (Prometheus Pull)
if settings.ENABLE_METRICS:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    # Auto-instrument FastAPI (Traces)
    FastAPIInstrumentor.instrument_app(app)

@app.get("/")
async def root():
    logger.info("Root accessed", extra={"user_agent": "unknown"})
    return {"message": "Observability Ready", "pod": settings.POD_NAME}

@app.get("/heavy")
def heavy_computation():
    total = sum(range(10000000))
    return {"result": total}