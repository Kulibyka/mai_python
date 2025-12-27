"""Интерактор для работы с местами."""

from collections.abc import Sequence

from lib.application.dto.place_dto import (
    PlaceCreateDTO,
    PlaceResponseDTO,
    PlaceSearchDTO,
    PlaceSearchResultDTO,
    PlaceUpdateDTO,
)
from lib.application.services.place_service import PlaceService
from lib.domain.value_objects import PlaceId


class CreatePlaceInteractor:
    """Интерактор для создания места."""

    def __init__(self, place_service: PlaceService) -> None:
        """
        Инициализирует интерактор.

        :param place_service: Сервис для работы с местами
        """
        self._place_service = place_service

    async def execute(self, dto: PlaceCreateDTO) -> PlaceResponseDTO:
        """
        Создает новое место.

        :param dto: DTO с данными для создания места
        :return: DTO созданного места
        """
        return await self._place_service.create_place(dto)


class GetPlaceInteractor:
    """Интерактор для получения места."""

    def __init__(self, place_service: PlaceService) -> None:
        """
        Инициализирует интерактор.

        :param place_service: Сервис для работы с местами
        """
        self._place_service = place_service

    async def execute(self, place_id: PlaceId) -> PlaceResponseDTO | None:
        """
        Получает место по идентификатору.

        :param place_id: Идентификатор места
        :return: DTO места или None, если не найдено
        """
        return await self._place_service.get_place(place_id)


class UpdatePlaceInteractor:
    """Интерактор для обновления места."""

    def __init__(self, place_service: PlaceService) -> None:
        """
        Инициализирует интерактор.

        :param place_service: Сервис для работы с местами
        """
        self._place_service = place_service

    async def execute(self, place_id: PlaceId, dto: PlaceUpdateDTO) -> PlaceResponseDTO | None:
        """
        Обновляет место.

        :param place_id: Идентификатор места
        :param dto: DTO с данными для обновления
        :return: DTO обновленного места или None, если не найдено
        """
        return await self._place_service.update_place(place_id, dto)


class DeletePlaceInteractor:
    """Интерактор для удаления места."""

    def __init__(self, place_service: PlaceService) -> None:
        """
        Инициализирует интерактор.

        :param place_service: Сервис для работы с местами
        """
        self._place_service = place_service

    async def execute(self, place_id: PlaceId) -> bool:
        """
        Удаляет место.

        :param place_id: Идентификатор места
        :return: True, если место было удалено, False если не найдено
        """
        return await self._place_service.delete_place(place_id)


class SearchPlacesInteractor:
    """Интерактор для поиска мест."""

    def __init__(self, place_service: PlaceService) -> None:
        """
        Инициализирует интерактор.

        :param place_service: Сервис для работы с местами
        """
        self._place_service = place_service

    async def execute(self, dto: PlaceSearchDTO) -> Sequence[PlaceSearchResultDTO]:
        """
        Ищет места по различным критериям.

        :param dto: DTO с параметрами поиска
        :return: Список результатов поиска
        """
        return await self._place_service.search_places(dto)


__all__ = [
    "CreatePlaceInteractor",
    "DeletePlaceInteractor",
    "GetPlaceInteractor",
    "SearchPlacesInteractor",
    "UpdatePlaceInteractor",
]
