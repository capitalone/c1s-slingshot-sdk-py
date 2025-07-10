"""Types used throughout this SDK."""

from __future__ import annotations

from typing import TypedDict, Union

JSON_TYPE = Union[dict[str, "JSON_TYPE"], list["JSON_TYPE"], str, int, float, bool, None]


class ProjectSchema(TypedDict):
    """Schema for a project in Slingshot."""

    created_at: str
    updated_at: str
    id: str
    name: str | None
    app_id: str | None
