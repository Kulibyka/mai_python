"""Модуль значимого объекта оценки рейтинга."""

from dataclasses import dataclass

MAX_RATING = 5.0
MIN_RATING = 1.0


@dataclass(frozen=True)
class RatingScore:
    """Оценка рейтинга в диапазоне от 1.0 до 5.0."""

    value: float

    def __post_init__(self) -> None:
        """Проверяет, что значение находится в допустимом диапазоне."""
        if not (MIN_RATING <= self.value <= MAX_RATING):
            msg = f"RatingScore must be between {MIN_RATING} and {MAX_RATING}"
            raise ValueError(msg)


__all__ = [
    "MAX_RATING",
    "MIN_RATING",
    "RatingScore",
]
