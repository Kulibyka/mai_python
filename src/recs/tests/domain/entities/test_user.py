"""Тесты для сущности пользователя."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from lib.domain.entities.user import User
from lib.domain.value_objects import Email, UserId, Username

UTC_PLUS_3 = timezone(timedelta(hours=3))


def test_user_creation_with_valid_data() -> None:
    """Тест создания User с валидными данными."""
    user_id = UserId(value=uuid4())
    email = Email(value="test@example.com")
    username = Username(value="testuser")
    created_at = datetime.now(UTC_PLUS_3)
    updated_at = datetime.now(UTC_PLUS_3)

    user = User(
        id=user_id,
        email=email,
        username=username,
        password_hash="hash",
        is_active=True,
        is_verified=False,
        profile={},
        preferences={},
        meta={},
        last_login_at=None,
        created_at=created_at,
        updated_at=updated_at,
    )
    assert user.id == user_id
    assert user.email == email
    assert user.username == username


def test_user_creation_with_none_email_and_username() -> None:
    """Тест создания User с None email и username."""
    user_id = UserId(value=uuid4())
    created_at = datetime.now(UTC_PLUS_3)
    updated_at = datetime.now(UTC_PLUS_3)

    user = User(
        id=user_id,
        email=None,
        username=None,
        password_hash=None,
        is_active=True,
        is_verified=False,
        profile={},
        preferences={},
        meta={},
        last_login_at=None,
        created_at=created_at,
        updated_at=updated_at,
    )
    assert user.email is None
    assert user.username is None


def test_user_equality() -> None:
    """Тест сравнения двух User с одинаковыми данными."""
    uuid_value = uuid4()
    user_id1 = UserId(value=uuid_value)
    user_id2 = UserId(value=uuid_value)
    email = Email(value="test@example.com")
    username = Username(value="testuser")
    created_at = datetime.now(UTC_PLUS_3)
    updated_at = datetime.now(UTC_PLUS_3)

    user1 = User(
        id=user_id1,
        email=email,
        username=username,
        password_hash="hash",
        is_active=True,
        is_verified=False,
        profile={},
        preferences={},
        meta={},
        last_login_at=None,
        created_at=created_at,
        updated_at=updated_at,
    )
    user2 = User(
        id=user_id2,
        email=email,
        username=username,
        password_hash="hash",
        is_active=True,
        is_verified=False,
        profile={},
        preferences={},
        meta={},
        last_login_at=None,
        created_at=created_at,
        updated_at=updated_at,
    )
    assert user1 == user2


def test_user_inequality_different_ids() -> None:
    """Тест сравнения двух User с разными ID."""
    user_id1 = UserId(value=uuid4())
    user_id2 = UserId(value=uuid4())
    email = Email(value="test@example.com")
    username = Username(value="testuser")
    created_at = datetime.now(UTC_PLUS_3)
    updated_at = datetime.now(UTC_PLUS_3)

    user1 = User(
        id=user_id1,
        email=email,
        username=username,
        password_hash="hash",
        is_active=True,
        is_verified=False,
        profile={},
        preferences={},
        meta={},
        last_login_at=None,
        created_at=created_at,
        updated_at=updated_at,
    )
    user2 = User(
        id=user_id2,
        email=email,
        username=username,
        password_hash="hash",
        is_active=True,
        is_verified=False,
        profile={},
        preferences={},
        meta={},
        last_login_at=None,
        created_at=created_at,
        updated_at=updated_at,
    )
    assert user1 != user2
