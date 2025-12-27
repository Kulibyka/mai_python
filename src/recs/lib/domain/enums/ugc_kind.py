"""Модуль перечисления типов пользовательского контента."""

from enum import Enum


class UgcKind(str, Enum):
    """Типы пользовательского контента (UGC - User Generated Content)."""

    RATING = "rating"
    REVIEW = "review"
    COMMENT = "comment"


__all__ = [
    "UgcKind",
]
