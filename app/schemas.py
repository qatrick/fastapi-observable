"""Global Pydantic schemas and custom base models."""

from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict


def datetime_to_iso_with_tz(dt: datetime) -> str:
    """
    Convert datetime to ISO format string with UTC timezone.

    Ensures all timestamps are timezone-aware and consistently formatted.
    """
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class CustomModel(BaseModel):
    """
    Custom base model with standardized datetime serialization.

    This model enforces consistent JSON encoding and provides
    utility methods for all subclasses.
    """

    model_config = ConfigDict(
        json_encoders={datetime: datetime_to_iso_with_tz},
        populate_by_name=True,
    )

    def serializable_dict(self, **kwargs) -> dict:
        """
        Return a dictionary containing only serializable fields.

        This method ensures all datetime fields are properly encoded
        before returning the dictionary.
        """
        default_dict = self.model_dump(**kwargs)
        return jsonable_encoder(default_dict)
