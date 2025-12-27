"""Модуль перечисления ролей пользователя."""

from enum import Enum


class RoleName(str, Enum):
    """Роли пользователя в системе."""

    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


__all__ = [
    "RoleName",
]
