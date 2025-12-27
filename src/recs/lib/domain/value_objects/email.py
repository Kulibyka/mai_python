"""Модуль значимого объекта email адреса."""

import re
from dataclasses import dataclass

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@dataclass(frozen=True)
class Email:
    """Email адрес пользователя с валидацией."""

    value: str

    def __post_init__(self) -> None:
        """Проверяет корректность email адреса."""
        if not self.value or not EMAIL_PATTERN.match(self.value):
            msg = f"Invalid email format: {self.value}"
            raise ValueError(msg)


__all__ = [
    "EMAIL_PATTERN",
    "Email",
]
