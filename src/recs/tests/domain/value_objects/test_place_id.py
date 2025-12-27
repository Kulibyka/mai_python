"""Тесты для значимого объекта идентификатора места."""

from dataclasses import FrozenInstanceError
from uuid import UUID, uuid4

import pytest

from lib.domain.value_objects import PlaceId


def test_place_id_creation_with_uuid() -> None:
    """Тест создания PlaceId с UUID."""
    uuid_value = uuid4()
    place_id = PlaceId(value=uuid_value)
    assert place_id.value == uuid_value
    assert isinstance(place_id.value, UUID)


def test_place_id_is_frozen() -> None:
    """Тест, что PlaceId является неизменяемым объектом."""
    place_id = PlaceId(value=uuid4())
    with pytest.raises(FrozenInstanceError):
        place_id.value = uuid4()  # pyright: ignore[reportAttributeAccessIssue]


def test_place_id_equality() -> None:
    """Тест сравнения двух PlaceId с одинаковыми значениями."""
    uuid_value = uuid4()
    place_id1 = PlaceId(value=uuid_value)
    place_id2 = PlaceId(value=uuid_value)
    assert place_id1 == place_id2


def test_place_id_inequality() -> None:
    """Тест сравнения двух PlaceId с разными значениями."""
    place_id1 = PlaceId(value=uuid4())
    place_id2 = PlaceId(value=uuid4())
    assert place_id1 != place_id2
