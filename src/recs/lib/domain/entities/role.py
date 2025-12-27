"""Модуль сущности роли."""

from dataclasses import dataclass
from datetime import datetime

from lib.domain.enums import RoleName
from lib.domain.value_objects import RoleId


@dataclass
class Role:
    """Модель роли пользователя в системе."""

    id: RoleId
    code: RoleName
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


__all__ = [
    "Role",
]
