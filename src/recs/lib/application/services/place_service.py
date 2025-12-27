"""Сервис для работы с местами."""

from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from sentence_transformers import SentenceTransformer

from lib.application.dto.place_dto import (
    PlaceCreateDTO,
    PlaceResponseDTO,
    PlaceSearchDTO,
    PlaceSearchResultDTO,
    PlaceUpdateDTO,
)
from lib.application.gateways.place_repository import IPlaceRepository
from lib.application.gateways.qdrant_place_repository import IQdrantPlaceRepository
from lib.domain.entities.place import Place
from lib.domain.value_objects import Coordinates, OsmId, PlaceId


class PlaceService:
    """Сервис для работы с местами."""

    # Константа для временной зоны UTC+3
    UTC_PLUS_3 = timezone(timedelta(hours=3))

    def __init__(
        self,
        place_repository: IPlaceRepository,
        qdrant_repository: IQdrantPlaceRepository,
        embedding_model: SentenceTransformer,
    ) -> None:
        """
        Инициализирует сервис мест.

        :param place_repository: Репозиторий мест в PostgreSQL
        :param qdrant_repository: Репозиторий мест в Qdrant для векторного поиска
        :param embedding_model: Модель для генерации эмбеддингов
        """
        self._place_repo = place_repository
        self._qdrant_repo = qdrant_repository
        self._embedding_model = embedding_model

    async def create_place(self, dto: PlaceCreateDTO) -> PlaceResponseDTO:
        """
        Создает новое место.

        :param dto: DTO с данными для создания места
        :return: DTO созданного места
        """
        # Создаем domain entity
        place_id = PlaceId(value=uuid4())
        osm_id = OsmId(value=dto.osm_id)
        coordinates = None
        if dto.latitude is not None and dto.longitude is not None:
            coordinates = Coordinates(latitude=dto.latitude, longitude=dto.longitude)

        now = datetime.now(self.UTC_PLUS_3)
        place = Place(
            id=place_id,
            osm_id=osm_id,
            osm_type=dto.osm_type,
            name=dto.name,
            category_key=dto.category_key,
            category_value=dto.category_value,
            coordinates=coordinates,
            tags=dto.tags,
            address=dto.address,
            source=dto.source,
            is_active=dto.is_active,
            created_at=now,
            updated_at=now,
        )

        # Сохраняем в PostgreSQL
        created_place = await self._place_repo.create(place)

        # Генерируем эмбеддинг и сохраняем в Qdrant
        if created_place.name:
            vector: list[float] = self._embedding_model.encode(created_place.name).tolist()  # type: ignore[return-value]
        else:
            vector = self._embedding_model.encode("Unknown place").tolist()  # type: ignore[return-value]

        payload = {
            "name": created_place.name,
            "category": created_place.category_value,
            "lat": float(created_place.coordinates.latitude) if created_place.coordinates else None,
            "lon": float(created_place.coordinates.longitude) if created_place.coordinates else None,
            "tags": created_place.tags,
        }

        await self._qdrant_repo.upsert_place(
            place_id=created_place.id,
            vector=vector,
            payload=payload,
        )

        return self._place_to_response_dto(created_place)

    async def get_place(self, place_id: PlaceId) -> PlaceResponseDTO | None:
        """
        Получает место по идентификатору.

        :param place_id: Идентификатор места
        :return: DTO места или None, если не найдено
        """
        place = await self._place_repo.get_by_id(place_id)
        return self._place_to_response_dto(place) if place else None

    async def update_place(self, place_id: PlaceId, dto: PlaceUpdateDTO) -> PlaceResponseDTO | None:
        """
        Обновляет место.

        :param place_id: Идентификатор места
        :param dto: DTO с данными для обновления
        :return: DTO обновленного места или None, если не найдено
        """
        place = await self._place_repo.get_by_id(place_id)
        if not place:
            return None

        self._apply_update_dto(place, dto)
        place.updated_at = datetime.now(self.UTC_PLUS_3)

        # Сохраняем в PostgreSQL
        updated_place = await self._place_repo.update(place)

        # Обновляем в Qdrant
        await self._sync_place_to_qdrant(updated_place)

        return self._place_to_response_dto(updated_place)

    def _apply_update_dto(self, place: Place, dto: PlaceUpdateDTO) -> None:  # noqa: C901
        """
        Применяет изменения из DTO к сущности места.

        :param place: Сущность места для обновления
        :param dto: DTO с данными для обновления
        """
        if dto.osm_type is not None:
            place.osm_type = dto.osm_type
        if dto.name is not None:
            place.name = dto.name
        if dto.category_key is not None:
            place.category_key = dto.category_key
        if dto.category_value is not None:
            place.category_value = dto.category_value
        if dto.latitude is not None and dto.longitude is not None:
            place.coordinates = Coordinates(latitude=dto.latitude, longitude=dto.longitude)
        elif dto.latitude is None and dto.longitude is None:
            place.coordinates = None
        if dto.tags is not None:
            place.tags = dto.tags
        if dto.address is not None:
            place.address = dto.address
        if dto.source is not None:
            place.source = dto.source
        if dto.is_active is not None:
            place.is_active = dto.is_active

    async def _sync_place_to_qdrant(self, place: Place) -> None:
        """
        Синхронизирует место с Qdrant.

        :param place: Сущность места для синхронизации
        """
        if place.name:
            vector: list[float] = self._embedding_model.encode(place.name).tolist()  # type: ignore[return-value]
        else:
            vector = self._embedding_model.encode("Unknown place").tolist()  # type: ignore[return-value]

        payload = {
            "name": place.name,
            "category": place.category_value,
            "lat": float(place.coordinates.latitude) if place.coordinates else None,
            "lon": float(place.coordinates.longitude) if place.coordinates else None,
            "tags": place.tags,
        }

        await self._qdrant_repo.upsert_place(
            place_id=place.id,
            vector=vector,
            payload=payload,
        )

    async def delete_place(self, place_id: PlaceId) -> bool:
        """
        Удаляет место.

        :param place_id: Идентификатор места
        :return: True, если место было удалено, False если не найдено
        """
        place = await self._place_repo.get_by_id(place_id)
        if not place:
            return False

        await self._place_repo.delete(place_id)
        await self._qdrant_repo.delete_place(place_id)
        return True

    async def search_places(self, dto: PlaceSearchDTO) -> Sequence[PlaceSearchResultDTO]:
        """
        Ищет места по различным критериям.

        :param dto: DTO с параметрами поиска
        :return: Список результатов поиска
        """
        # Векторный поиск (приоритет, если есть query или vector)
        if dto.query or dto.vector:
            results = await self._search_by_vector(dto)
            if results:
                return results

        # Поиск по категории
        if dto.category_key or dto.category_value:
            return await self._search_by_category(dto)

        # Поиск по координатам
        if dto.latitude is not None and dto.longitude is not None and dto.radius_km is not None:
            return await self._search_by_coordinates(dto)

        # Поиск по названию (если указан query, но нет vector)
        if dto.query:
            return await self._search_by_name(dto)

        return []

    async def _search_by_vector(self, dto: PlaceSearchDTO) -> list[PlaceSearchResultDTO]:
        """
        Выполняет векторный поиск мест.

        :param dto: DTO с параметрами поиска
        :return: Список результатов поиска
        """
        vector: list[float] | None = dto.vector
        if not vector and dto.query:
            vector = self._embedding_model.encode(dto.query).tolist()  # type: ignore[return-value]

        if not vector:
            return []

        filter_conditions: dict[str, Any] = {}
        if dto.category_key:
            filter_conditions["category_key"] = dto.category_key
        if dto.category_value:
            filter_conditions["category"] = dto.category_value

        qdrant_results = await self._qdrant_repo.search_by_vector(
            vector=vector,
            limit=dto.limit,
            score_threshold=dto.score_threshold,
            filter_conditions=filter_conditions if filter_conditions else None,
        )

        return [
            PlaceSearchResultDTO(
                place=self._place_to_response_dto(place),
                score=score,
            )
            for place, score in qdrant_results
        ]

    async def _search_by_category(self, dto: PlaceSearchDTO) -> list[PlaceSearchResultDTO]:
        """
        Выполняет поиск мест по категории.

        :param dto: DTO с параметрами поиска
        :return: Список результатов поиска
        """
        places = await self._place_repo.search_by_category(
            category_key=dto.category_key,
            category_value=dto.category_value,
            limit=dto.limit,
            offset=dto.offset,
        )
        return [
            PlaceSearchResultDTO(
                place=self._place_to_response_dto(place),
                score=None,
            )
            for place in places
        ]

    async def _search_by_coordinates(self, dto: PlaceSearchDTO) -> list[PlaceSearchResultDTO]:
        """
        Выполняет поиск мест по координатам.

        :param dto: DTO с параметрами поиска
        :return: Список результатов поиска
        """
        if dto.latitude is None or dto.longitude is None or dto.radius_km is None:
            return []

        places = await self._place_repo.search_by_coordinates(
            latitude=dto.latitude,
            longitude=dto.longitude,
            radius_km=dto.radius_km,
            limit=dto.limit,
        )
        return [
            PlaceSearchResultDTO(
                place=self._place_to_response_dto(place),
                score=None,
            )
            for place in places
        ]

    async def _search_by_name(self, dto: PlaceSearchDTO) -> list[PlaceSearchResultDTO]:
        """
        Выполняет поиск мест по названию.

        :param dto: DTO с параметрами поиска
        :return: Список результатов поиска
        """
        if not dto.query:
            return []

        places = await self._place_repo.search_by_name(name=dto.query, limit=dto.limit)
        return [
            PlaceSearchResultDTO(
                place=self._place_to_response_dto(place),
                score=None,
            )
            for place in places
        ]

    def _place_to_response_dto(self, place: Place) -> PlaceResponseDTO:
        """
        Преобразует domain entity в DTO ответа.

        :param place: Domain entity места
        :return: DTO ответа
        """
        return PlaceResponseDTO(
            id=place.id.value,
            osm_id=place.osm_id.value,
            osm_type=place.osm_type,
            name=place.name,
            category_key=place.category_key,
            category_value=place.category_value,
            latitude=place.coordinates.latitude if place.coordinates else None,
            longitude=place.coordinates.longitude if place.coordinates else None,
            tags=place.tags,
            address=place.address,
            source=place.source,
            is_active=place.is_active,
            created_at=place.created_at.isoformat(),
            updated_at=place.updated_at.isoformat(),
        )


__all__ = [
    "PlaceService",
]
