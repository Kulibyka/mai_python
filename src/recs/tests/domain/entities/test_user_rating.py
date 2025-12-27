"""Тесты для сущности рейтинга пользователя."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from lib.domain.entities.user_rating import UserRating
from lib.domain.value_objects import PlaceId, RatingScore, UserId

UTC_PLUS_3 = timezone(timedelta(hours=3))


def test_user_rating_creation_with_valid_data() -> None:
    """Тест создания UserRating с валидными данными."""
    user_id = UserId(value=uuid4())
    place_id = PlaceId(value=uuid4())
    score = RatingScore(value=4.5)
    created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC_PLUS_3)

    rating = UserRating(
        user_id=user_id,
        place_id=place_id,
        score=score,
        created_at=created_at,
    )

    assert rating.user_id == user_id
    assert rating.place_id == place_id
    assert rating.score == score
    assert rating.created_at == created_at
    assert rating.comment is None


def test_user_rating_creation_with_comment() -> None:
    """Тест создания UserRating с комментарием."""
    from uuid import uuid4

    user_id = UserId(value=uuid4())
    place_id = PlaceId(value=uuid4())
    score = RatingScore(value=4.5)
    created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC_PLUS_3)
    comment = "Отличное место!"

    rating = UserRating(
        user_id=user_id,
        place_id=place_id,
        score=score,
        created_at=created_at,
        comment=comment,
    )

    assert rating.comment == comment


def test_user_rating_equality() -> None:
    """Тест сравнения двух UserRating с одинаковыми данными."""
    from uuid import uuid4

    user_id = UserId(value=uuid4())
    place_id = PlaceId(value=uuid4())
    score = RatingScore(value=4.5)
    created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC_PLUS_3)

    rating1 = UserRating(
        user_id=user_id,
        place_id=place_id,
        score=score,
        created_at=created_at,
    )

    rating2 = UserRating(
        user_id=user_id,
        place_id=place_id,
        score=score,
        created_at=created_at,
    )

    assert rating1 == rating2


def test_user_rating_inequality_different_scores() -> None:
    """Тест сравнения двух UserRating с разными оценками."""
    from uuid import uuid4

    user_id = UserId(value=uuid4())
    place_id = PlaceId(value=uuid4())
    score1 = RatingScore(value=4.5)
    score2 = RatingScore(value=3.0)
    created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC_PLUS_3)

    rating1 = UserRating(
        user_id=user_id,
        place_id=place_id,
        score=score1,
        created_at=created_at,
    )

    rating2 = UserRating(
        user_id=user_id,
        place_id=place_id,
        score=score2,
        created_at=created_at,
    )

    assert rating1 != rating2


def test_user_rating_inequality_different_users() -> None:
    """Тест сравнения двух UserRating от разных пользователей."""
    from uuid import uuid4

    user_id1 = UserId(value=uuid4())
    user_id2 = UserId(value=uuid4())
    place_id = PlaceId(value=uuid4())
    score = RatingScore(value=4.5)
    created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC_PLUS_3)

    rating1 = UserRating(
        user_id=user_id1,
        place_id=place_id,
        score=score,
        created_at=created_at,
    )

    rating2 = UserRating(
        user_id=user_id2,
        place_id=place_id,
        score=score,
        created_at=created_at,
    )

    assert rating1 != rating2


def test_user_rating_inequality_different_places() -> None:
    """Тест сравнения двух UserRating для разных мест."""
    from uuid import uuid4

    user_id = UserId(value=uuid4())
    place_id1 = PlaceId(value=uuid4())
    place_id2 = PlaceId(value=uuid4())
    score = RatingScore(value=4.5)
    created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC_PLUS_3)

    rating1 = UserRating(
        user_id=user_id,
        place_id=place_id1,
        score=score,
        created_at=created_at,
    )

    rating2 = UserRating(
        user_id=user_id,
        place_id=place_id2,
        score=score,
        created_at=created_at,
    )

    assert rating1 != rating2


def test_user_rating_with_empty_comment() -> None:
    """Тест создания UserRating с пустым комментарием."""
    from uuid import uuid4

    user_id = UserId(value=uuid4())
    place_id = PlaceId(value=uuid4())
    score = RatingScore(value=4.5)
    created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC_PLUS_3)

    rating = UserRating(
        user_id=user_id,
        place_id=place_id,
        score=score,
        created_at=created_at,
        comment="",
    )

    assert rating.comment == ""


def test_user_rating_comment_modification() -> None:
    """Тест изменения комментария в UserRating."""
    from uuid import uuid4

    user_id = UserId(value=uuid4())
    place_id = PlaceId(value=uuid4())
    score = RatingScore(value=4.5)
    created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC_PLUS_3)

    rating = UserRating(
        user_id=user_id,
        place_id=place_id,
        score=score,
        created_at=created_at,
        comment="Старый комментарий",
    )

    rating.comment = "Новый комментарий"
    assert rating.comment == "Новый комментарий"
