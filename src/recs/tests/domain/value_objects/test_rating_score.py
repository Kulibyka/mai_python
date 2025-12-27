"""Тесты для значимого объекта оценки рейтинга."""

from dataclasses import FrozenInstanceError

import pytest

from lib.domain.value_objects import MAX_RATING, MIN_RATING, RatingScore


@pytest.mark.parametrize(
    "value",
    [1.0, 2.5, 3.5, 5.0, MIN_RATING, MAX_RATING],
)
def test_rating_score_creation_with_valid_value(value: float) -> None:
    """Тест создания RatingScore с валидными значениями."""
    score = RatingScore(value=value)
    assert score.value == value


@pytest.mark.parametrize("invalid_value", [0.9, 5.1, -1.0, 10.0, 0.0])
def test_rating_score_raises_error_for_invalid_value(invalid_value: float) -> None:
    """Тест, что RatingScore выбрасывает ошибку при невалидном значении."""
    with pytest.raises(ValueError, match="RatingScore must be between"):
        RatingScore(value=invalid_value)


def test_rating_score_is_frozen():
    """Тест, что RatingScore является неизменяемым объектом."""
    score = RatingScore(value=3.0)
    with pytest.raises(FrozenInstanceError):
        score.value = 4.0  # pyright: ignore[reportAttributeAccessIssue]


@pytest.mark.parametrize("value", [1.0, 2.5, 3.5, 5.0])
def test_rating_score_equality(value: float) -> None:
    """Тест сравнения двух RatingScore с одинаковыми значениями."""
    score1 = RatingScore(value=value)
    score2 = RatingScore(value=value)
    assert score1 == score2


@pytest.mark.parametrize(
    ("value1", "value2"),
    [(1.0, 5.0), (2.5, 3.5), (1.0, 4.0), (3.0, 4.5)],
)
def test_rating_score_inequality(value1: float, value2: float) -> None:
    """Тест сравнения двух RatingScore с разными значениями."""
    score1 = RatingScore(value=value1)
    score2 = RatingScore(value=value2)
    assert score1 != score2


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (2.5, 2.5),
        (2.5000001, 2.5000001),
    ],
)
def test_rating_score_with_float_precision(
    value: float,
    expected: float,
) -> None:
    """Тест создания RatingScore с различной точностью float."""
    score = RatingScore(value=value)
    assert score.value == expected
