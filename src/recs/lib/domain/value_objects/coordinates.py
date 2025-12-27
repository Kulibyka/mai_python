"""Модуль значимого объекта географических координат."""

from dataclasses import dataclass
from decimal import Decimal

MIN_LATITUDE = Decimal("-90.0")
MAX_LATITUDE = Decimal("90.0")
MIN_LONGITUDE = Decimal("-180.0")
MAX_LONGITUDE = Decimal("180.0")


@dataclass(frozen=True)
class Coordinates:
    """Географические координаты (широта и долгота)."""

    latitude: Decimal
    longitude: Decimal

    def __post_init__(self) -> None:
        """Проверяет корректность координат."""
        if not (MIN_LATITUDE <= self.latitude <= MAX_LATITUDE):
            msg = f"Latitude must be between {MIN_LATITUDE} and {MAX_LATITUDE}"
            raise ValueError(msg)
        if not (MIN_LONGITUDE <= self.longitude <= MAX_LONGITUDE):
            msg = f"Longitude must be between {MIN_LONGITUDE} and {MAX_LONGITUDE}"
            raise ValueError(msg)


__all__ = [
    "MAX_LATITUDE",
    "MAX_LONGITUDE",
    "MIN_LATITUDE",
    "MIN_LONGITUDE",
    "Coordinates",
]
