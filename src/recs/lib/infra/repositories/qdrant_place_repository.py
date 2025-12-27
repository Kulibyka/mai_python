"""Реализация репозитория мест в Qdrant для векторного поиска."""

from typing import Any
from uuid import UUID

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Filter, PointStruct

from lib.application.gateways.qdrant_place_repository import IQdrantPlaceRepository
from lib.domain.entities.place import Place
from lib.domain.value_objects import PlaceId
from lib.infra.repositories.place_repository import SQLAlchemyPlaceRepository
from lib.main.settings import QdrantSettings


class QdrantPlaceRepository(IQdrantPlaceRepository):
    """Реализация репозитория мест в Qdrant для векторного поиска."""

    def __init__(
        self,
        client: AsyncQdrantClient,
        settings: QdrantSettings,
        postgres_repo: SQLAlchemyPlaceRepository,
    ) -> None:
        """
        Инициализирует репозиторий Qdrant.

        :param client: Клиент Qdrant
        :param settings: Настройки Qdrant
        :param postgres_repo: Репозиторий PostgreSQL для получения полных данных мест
        """
        self._client = client
        self._collection_name = settings.collection_name
        self._postgres_repo = postgres_repo

    async def search_by_vector(
        self,
        vector: list[float],
        limit: int = 10,
        score_threshold: float | None = None,
        filter_conditions: dict[str, Any] | None = None,
    ) -> list[tuple[Place, float]]:
        """Ищет места по вектору эмбеддинга."""
        # Строим фильтр из условий
        qdrant_filter = None
        if filter_conditions:
            # TODO: Реализовать построение Filter из dict  # noqa: FIX002, TD002, TD003
            # Пока используем простой подход
            qdrant_filter = Filter(must=[])

        # Выполняем поиск в Qdrant (асинхронный вызов)
        search_results = await self._client.search(  # type: ignore[attr-defined]
            collection_name=self._collection_name,
            query_vector=vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=qdrant_filter,
        )

        # Получаем полные данные мест из PostgreSQL
        results: list[tuple[Place, float]] = []
        for scored_point in search_results:  # type: ignore[assignment]
            # Qdrant возвращает ID как int или str, нужно преобразовать в UUID
            # Предполагаем, что ID в Qdrant соответствует PlaceId.value (UUID)
            try:
                point_id = str(scored_point.id) if not isinstance(scored_point.id, str) else scored_point.id  # type: ignore[attr-defined]
                place_id = PlaceId(value=UUID(point_id))
            except (ValueError, TypeError):
                # Если не удалось преобразовать, пропускаем
                continue

            place = await self._postgres_repo.get_by_id(place_id)
            if place:
                score = float(scored_point.score) if hasattr(scored_point, "score") else 0.0  # type: ignore[attr-defined]
                results.append((place, score))

        return results

    async def upsert_place(
        self,
        place_id: PlaceId,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        """Добавляет или обновляет место в Qdrant."""
        point = PointStruct(
            id=str(place_id.value),  # Qdrant принимает строковые ID
            vector=vector,
            payload=payload,
        )
        # Асинхронный вызов Qdrant
        await self._client.upsert(
            collection_name=self._collection_name,
            points=[point],
        )

    async def upsert_places(
        self,
        places: list[tuple[PlaceId, list[float], dict[str, Any]]],
    ) -> None:
        """Массовое добавление или обновление мест в Qdrant."""
        points = [
            PointStruct(
                id=str(place_id.value),
                vector=vector,
                payload=payload,
            )
            for place_id, vector, payload in places
        ]
        # Асинхронный вызов Qdrant
        await self._client.upsert(
            collection_name=self._collection_name,
            points=points,
        )

    async def delete_place(self, place_id: PlaceId) -> None:
        """Удаляет место из Qdrant."""
        # Асинхронный вызов Qdrant
        await self._client.delete(
            collection_name=self._collection_name,
            points_selector=[str(place_id.value)],
        )

    async def delete_places(self, place_ids: list[PlaceId]) -> None:
        """Массовое удаление мест из Qdrant."""
        # Асинхронный вызов Qdrant
        await self._client.delete(
            collection_name=self._collection_name,
            points_selector=[str(place_id.value) for place_id in place_ids],
        )


__all__ = [
    "QdrantPlaceRepository",
]
