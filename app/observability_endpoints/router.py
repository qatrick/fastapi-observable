"""Observability test endpoints."""

import logging
import time

from fastapi import APIRouter, status
from fastapi.concurrency import run_in_threadpool

from app.config import settings
from .schemas import ComputationResult, SimpleResponse
from .service import perform_heavy_computation, perform_light_computation

logger = logging.getLogger("app")
router = APIRouter(prefix="/observability", tags=["observability"])


@router.get(
    "/root",
    response_model=SimpleResponse,
    status_code=status.HTTP_200_OK,
    description="Root endpoint for testing observability",
)
async def root() -> SimpleResponse:
    """Root endpoint for basic observability testing."""
    logger.info("Root accessed", extra={"user_agent": "unknown"})
    return SimpleResponse(message="Observability Ready", pod=settings.POD_NAME)


@router.get(
    "/heavy",
    response_model=ComputationResult,
    status_code=status.HTTP_200_OK,
    description="CPU-intensive computation endpoint",
    summary="Heavy Computation",
)
async def heavy_computation() -> ComputationResult:
    """
    Perform a CPU-intensive computation in thread pool.

    This endpoint demonstrates running CPU-bound work without blocking
    the async event loop by using run_in_threadpool.
    """
    start = time.time()
    result = await run_in_threadpool(perform_heavy_computation)
    duration = (time.time() - start) * 1000

    logger.info(f"Heavy computation completed in {duration:.2f}ms")

    return ComputationResult(
        result=result,
        computation_type="cpu-intensive",
        duration_ms=duration,
    )


@router.get(
    "/light",
    response_model=ComputationResult,
    status_code=status.HTTP_200_OK,
    description="Lightweight async computation endpoint",
    summary="Light Computation",
)
async def light_computation() -> ComputationResult:
    """
    Perform a lightweight async computation.

    This endpoint demonstrates non-blocking async I/O operations.
    """
    start = time.time()
    result = await perform_light_computation()
    duration = (time.time() - start) * 1000

    return ComputationResult(
        result=result,
        computation_type="async",
        duration_ms=duration,
    )
