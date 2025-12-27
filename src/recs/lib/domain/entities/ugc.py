"""Модуль сущности пользовательского контента."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from lib.domain.enums import UgcKind
from lib.domain.value_objects import PlaceId, RatingScore, UserId


@dataclass
class UGC:
    """Модель пользовательского контента (рейтинг, отзыв, комментарий)."""

    id: UUID
    user_id: UserId
    place_id: PlaceId
    kind: UgcKind
    rating: RatingScore | None
    text: str | None
    meta: dict[str, Any]
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        """Проверяет бизнес-правила."""
        # Для рейтинга должен быть указан rating
        if self.kind == UgcKind.RATING and self.rating is None:
            raise ValueError("Rating is required for RATING kind")
        # Для отзыва должен быть указан текст
        if self.kind == UgcKind.REVIEW and not self.text:
            raise ValueError("Text is required for REVIEW kind")


__all__ = [
    "UGC",
]
