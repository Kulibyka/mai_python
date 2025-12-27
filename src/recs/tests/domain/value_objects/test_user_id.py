"""Тесты для значимого объекта идентификатора пользователя."""

from dataclasses import FrozenInstanceError
from uuid import UUID, uuid4

import pytest

from lib.domain.value_objects import UserId


def test_user_id_creation_with_uuid() -> None:
    """Тест создания UserId с UUID."""
    uuid_value = uuid4()
    user_id = UserId(value=uuid_value)
    assert user_id.value == uuid_value
    assert isinstance(user_id.value, UUID)


def test_user_id_is_frozen() -> None:
    """Тест, что UserId является неизменяемым объектом."""
    user_id = UserId(value=uuid4())
    with pytest.raises(FrozenInstanceError):
        user_id.value = uuid4()  # pyright: ignore[reportAttributeAccessIssue]


def test_user_id_equality() -> None:
    """Тест сравнения двух UserId с одинаковыми значениями."""
    uuid_value = uuid4()
    user_id1 = UserId(value=uuid_value)
    user_id2 = UserId(value=uuid_value)
    assert user_id1 == user_id2


def test_user_id_inequality() -> None:
    """Тест сравнения двух UserId с разными значениями."""
    user_id1 = UserId(value=uuid4())
    user_id2 = UserId(value=uuid4())
    assert user_id1 != user_id2
