"""Health check utility functions."""

from datetime import datetime
from zoneinfo import ZoneInfo


def get_current_timestamp_iso() -> str:
    """Get current timestamp in ISO format with UTC timezone."""
    return datetime.now(ZoneInfo("UTC")).isoformat()
