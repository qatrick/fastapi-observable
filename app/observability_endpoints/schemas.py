"""Observability endpoints schemas."""

from app.schemas import CustomModel


class ComputationResult(CustomModel):
    """Computation result response model."""

    result: int
    computation_type: str
    duration_ms: float


class SimpleResponse(CustomModel):
    """Simple message response."""

    message: str
    pod: str
