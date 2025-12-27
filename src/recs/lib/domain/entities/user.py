"""Модуль сущности пользователя."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from lib.domain.value_objects import Email, UserId, Username


@dataclass
class User:
    """Модель пользователя."""

    id: UserId
    email: Email | None
    username: Username | None
    password_hash: str | None
    is_active: bool
    is_verified: bool
    profile: dict[str, Any]
    preferences: dict[str, Any]
    meta: dict[str, Any]
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime


__all__ = [
    "User",
]
