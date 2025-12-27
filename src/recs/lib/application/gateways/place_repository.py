"""Интерфейс репозитория мест."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from decimal import Decimal

from lib.domain.entities.place import Place
from lib.domain.value_objects import OsmId, PlaceId


class IPlaceRepository(ABC):
    """Интерфейс репозитория для работы с местами."""

    @abstractmethod
    async def get_by_id(self, place_id: PlaceId) -> Place | None:
        """
        Получает место по идентификатору.

        :param place_id: Идентификатор места
        :return: Место или None, если не найдено
        """
        ...

    @abstractmethod
    async def get_by_osm_id(self, osm_id: OsmId) -> Place | None:
        """
        Получает место по OSM идентификатору.

        :param osm_id: OSM идентификатор
        :return: Место или None, если не найдено
        """
        ...

    @abstractmethod
    async def search_by_name(self, name: str, limit: int = 10) -> Sequence[Place]:
        """
        Ищет места по названию.

        :param name: Часть названия для поиска
        :param limit: Максимальное количество результатов
        :return: Список найденных мест
        """
        ...

    @abstractmethod
    async def search_by_category(
        self,
        category_key: str | None = None,
        category_value: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Sequence[Place]:
        """
        Ищет места по категории.

        :param category_key: Ключ категории
        :param category_value: Значение категории
        :param limit: Максимальное количество результатов
        :param offset: Смещение для пагинации
        :return: Список найденных мест
        """
        ...

    @abstractmethod
    async def search_by_coordinates(
        self,
        latitude: Decimal,
        longitude: Decimal,
        radius_km: Decimal,
        limit: int = 10,
    ) -> Sequence[Place]:
        """
        Ищет места в радиусе от указанных координат.

        :param latitude: Широта центра поиска
        :param longitude: Долгота центра поиска
        :param radius_km: Радиус поиска в километрах
        :param limit: Максимальное количество результатов
        :return: Список найденных мест
        """
        ...

    @abstractmethod
    async def create(self, place: Place) -> Place:
        """
        Создает новое место.

        :param place: Место для создания
        :return: Созданное место
        """
        ...

    @abstractmethod
    async def update(self, place: Place) -> Place:
        """
        Обновляет существующее место.

        :param place: Место для обновления
        :return: Обновленное место
        """
        ...

    @abstractmethod
    async def delete(self, place_id: PlaceId) -> None:
        """
        Удаляет место.

        :param place_id: Идентификатор места для удаления
        """
        ...


__all__ = [
    "IPlaceRepository",
]
