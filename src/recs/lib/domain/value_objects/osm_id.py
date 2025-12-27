"""Модуль значимого объекта OSM идентификатора."""

from dataclasses import dataclass

MAX_OSM_ID_LENGTH = 64


@dataclass(frozen=True)
class OsmId:
    """Идентификатор объекта из OpenStreetMap (например, 'node:61669376')."""

    value: str

    def __post_init__(self) -> None:
        """Проверяет корректность OSM идентификатора."""
        if not self.value:
            raise ValueError("OsmId cannot be empty")
        if len(self.value) > MAX_OSM_ID_LENGTH:
            msg = f"OsmId cannot exceed {MAX_OSM_ID_LENGTH} characters"
            raise ValueError(msg)


__all__ = [
    "MAX_OSM_ID_LENGTH",
    "OsmId",
]
