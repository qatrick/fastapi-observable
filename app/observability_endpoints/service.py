"""Observability endpoints business logic."""

import time


def perform_heavy_computation() -> int:
    """
    Perform a CPU-intensive computation.

    In production, this should be offloaded to background workers
    to avoid blocking the event loop.
    """
    start = time.time()
    result = sum(range(10000000))
    duration = (time.time() - start) * 1000
    return result


async def perform_light_computation() -> int:
    """Perform a lightweight async computation."""
    return sum(range(10000))
