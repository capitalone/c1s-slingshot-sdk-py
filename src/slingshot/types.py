"""Types used throughout this SDK."""

from typing import Optional, TypedDict, Union

JSON_TYPE = Union[dict[str, "JSON_TYPE"], list["JSON_TYPE"], str, int, float, bool, None]


class ProjectSchema(TypedDict):
    """Schema for a project in Slingshot."""

    created_at: str
    updated_at: str
    id: str
    name: Optional[str]
    app_id: Optional[str]
