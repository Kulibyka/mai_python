"""Модуль сущности места."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from lib.domain.value_objects import Coordinates, OsmId, PlaceId


@dataclass
class Place:
    """Модель места (точки интереса) из OpenStreetMap."""

    id: PlaceId
    osm_id: OsmId
    osm_type: str | None
    name: str | None
    category_key: str | None
    category_value: str | None
    coordinates: Coordinates | None
    tags: dict[str, Any]
    address: dict[str, Any]
    source: dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime


__all__ = [
    "Place",
]
