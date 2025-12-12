"""FastAPI application factory and middleware setup."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import make_asgi_app

from .config import settings
from .logger import setup_logging
from .observability import setup_profiling, setup_tracing
from .health.router import router as health_router
from .observability_endpoints.router import router as observability_router

# Setup logging first
setup_logging(settings.APP_NAME, settings.ENV)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} in {settings.ENV}")
    setup_tracing()
    setup_profiling()
    yield
    logger.info("Shutting down")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise-grade FastAPI with observability",
    lifespan=lifespan,
)

# Mount Prometheus metrics endpoint
if settings.ENABLE_METRICS:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    # Auto-instrument FastAPI for tracing
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.instrument_app(app)

# Include routers with explicit module prefixes for clarity
app.include_router(health_router)
app.include_router(observability_router)
