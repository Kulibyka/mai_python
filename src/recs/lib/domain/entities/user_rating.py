"""Модуль сущности рейтинга пользователя."""

from dataclasses import dataclass
from datetime import datetime

from lib.domain.value_objects import PlaceId, RatingScore, UserId


@dataclass
class UserRating:
    """
    Модель рейтинга, который пользователь поставил месту.

    Это упрощенная модель для обратной совместимости.
    Для полной функциональности используйте UGC entity.
    """

    user_id: UserId
    place_id: PlaceId
    score: RatingScore
    created_at: datetime
    comment: str | None = None


__all__ = [
    "UserRating",
]
