"""Модуль значимого объекта идентификатора места."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class PlaceId:
    """Уникальный идентификатор места."""

    value: UUID


__all__ = [
    "PlaceId",
]
