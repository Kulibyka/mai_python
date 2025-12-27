"""Интерфейс репозитория мест в Qdrant для векторного поиска."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from lib.domain.entities.place import Place
from lib.domain.value_objects import PlaceId


class IQdrantPlaceRepository(ABC):
    """Интерфейс репозитория для работы с местами в Qdrant (векторный поиск)."""

    @abstractmethod
    async def search_by_vector(
        self,
        vector: list[float],
        limit: int = 10,
        score_threshold: float | None = None,
        filter_conditions: dict[str, Any] | None = None,
    ) -> Sequence[tuple[Place, float]]:
        """
        Ищет места по вектору эмбеддинга.

        :param vector: Вектор эмбеддинга для поиска
        :param limit: Максимальное количество результатов
        :param score_threshold: Минимальный порог схожести (0-1)
        :param filter_conditions: Условия фильтрации по payload
        :return: Список кортежей (место, score)
        """
        ...

    @abstractmethod
    async def upsert_place(
        self,
        place_id: PlaceId,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        """
        Добавляет или обновляет место в Qdrant.

        :param place_id: Идентификатор места
        :param vector: Вектор эмбеддинга
        :param payload: Метаданные места (name, category, lat, lon, tags)
        """
        ...

    @abstractmethod
    async def upsert_places(
        self,
        places: list[tuple[PlaceId, list[float], dict[str, Any]]],
    ) -> None:
        """
        Массовое добавление или обновление мест в Qdrant.

        :param places: Список кортежей (place_id, vector, payload)
        """
        ...

    @abstractmethod
    async def delete_place(self, place_id: PlaceId) -> None:
        """
        Удаляет место из Qdrant.

        :param place_id: Идентификатор места
        """
        ...

    @abstractmethod
    async def delete_places(self, place_ids: list[PlaceId]) -> None:
        """
        Массовое удаление мест из Qdrant.

        :param place_ids: Список идентификаторов мест
        """
        ...


__all__ = [
    "IQdrantPlaceRepository",
]
