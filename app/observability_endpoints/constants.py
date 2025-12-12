"""Observability endpoints constants."""

from enum import Enum


class ComputationLevel(str, Enum):
    """Computation intensity levels."""

    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
