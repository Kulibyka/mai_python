"""Модуль значимого объекта имени пользователя."""

from dataclasses import dataclass

MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 64


@dataclass(frozen=True)
class Username:
    """Имя пользователя с валидацией."""

    value: str

    def __post_init__(self) -> None:
        """Проверяет корректность имени пользователя."""
        if not self.value:
            raise ValueError("Username cannot be empty")
        if not (MIN_USERNAME_LENGTH <= len(self.value) <= MAX_USERNAME_LENGTH):
            msg = f"Username must be between {MIN_USERNAME_LENGTH} and {MAX_USERNAME_LENGTH} characters"
            raise ValueError(msg)


__all__ = [
    "MAX_USERNAME_LENGTH",
    "MIN_USERNAME_LENGTH",
    "Username",
]
