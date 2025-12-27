"""Модуль значимого объекта идентификатора пользователя."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UserId:
    """Уникальный идентификатор пользователя."""

    value: UUID


__all__ = [
    "UserId",
]
