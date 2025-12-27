"""Модуль значимого объекта идентификатора роли."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RoleId:
    """Уникальный идентификатор роли."""

    value: UUID


__all__ = [
    "RoleId",
]
