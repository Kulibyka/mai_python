"""Реализация репозитория мест."""

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from lib.application.gateways.place_repository import IPlaceRepository
from lib.domain.entities.place import Place
from lib.domain.value_objects import OsmId, PlaceId
from lib.infra.db.orm_models.place import PlaceORM, place_table


class SQLAlchemyPlaceRepository(IPlaceRepository):
    """Реализация репозитория мест на SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализирует репозиторий с сессией SQLAlchemy.

        :param session: Асинхронная сессия SQLAlchemy
        """
        self._session = session

    async def get_by_id(self, place_id: PlaceId) -> Place | None:
        """Получает место по идентификатору."""
        stmt = select(PlaceORM).where(place_table.c.id == place_id.value)
        result = await self._session.execute(stmt)
        orm_place = result.scalar_one_or_none()
        return orm_place.to_domain() if orm_place else None

    async def get_by_osm_id(self, osm_id: OsmId) -> Place | None:
        """Получает место по OSM идентификатору."""
        stmt = select(PlaceORM).where(place_table.c.osm_id == osm_id.value)
        result = await self._session.execute(stmt)
        orm_place = result.scalar_one_or_none()
        return orm_place.to_domain() if orm_place else None

    async def search_by_name(self, name: str, limit: int = 10) -> list[Place]:
        """Ищет места по названию."""
        stmt = (
            select(PlaceORM)
            .where(place_table.c.name.ilike(f"%{name}%"))
            .where(place_table.c.is_active == True)  # noqa: E712
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        orm_places = result.scalars().all()
        return [orm_place.to_domain() for orm_place in orm_places]

    async def search_by_category(
        self,
        category_key: str | None = None,
        category_value: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Place]:
        """Ищет места по категории."""
        stmt = select(PlaceORM).where(place_table.c.is_active == True)  # noqa: E712
        if category_key:
            stmt = stmt.where(place_table.c.category_key == category_key)
        if category_value:
            stmt = stmt.where(place_table.c.category_value == category_value)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        orm_places = result.scalars().all()
        return [orm_place.to_domain() for orm_place in orm_places]

    async def search_by_coordinates(
        self,
        latitude: Decimal,
        longitude: Decimal,
        radius_km: Decimal,
        limit: int = 10,
    ) -> list[Place]:
        """
        Ищет места в радиусе от указанных координат.

        Использует формулу гаверсинуса для расчета расстояния.
        Упрощенный расчет расстояния (для точности нужна полная формула гаверсинуса).
        Используем приблизительный расчет: 1 градус ≈ 111 км.
        """
        stmt = (
            select(PlaceORM)
            .where(place_table.c.lat.is_not(None))
            .where(place_table.c.lon.is_not(None))
            .where(place_table.c.is_active == True)  # noqa: E712
            .where(
                func.sqrt(
                    func.pow((place_table.c.lat - latitude) * Decimal("111.0"), 2)
                    + func.pow((place_table.c.lon - longitude) * Decimal("111.0"), 2),
                )
                <= radius_km,
            )
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        orm_places = result.scalars().all()
        return [orm_place.to_domain() for orm_place in orm_places]

    async def create(self, place: Place) -> Place:
        """Создает новое место."""
        orm_place = PlaceORM.from_domain(place)
        self._session.add(orm_place)
        await self._session.flush()
        await self._session.refresh(orm_place)
        return orm_place.to_domain()

    async def update(self, place: Place) -> Place:
        """Обновляет существующее место."""
        stmt = select(PlaceORM).where(place_table.c.id == place.id.value)
        result = await self._session.execute(stmt)
        orm_place = result.scalar_one()
        orm_place.osm_id = place.osm_id.value
        orm_place.osm_type = place.osm_type
        orm_place.name = place.name
        orm_place.category_key = place.category_key
        orm_place.category_value = place.category_value
        orm_place.lat = place.coordinates.latitude if place.coordinates else None
        orm_place.lon = place.coordinates.longitude if place.coordinates else None
        orm_place.tags = place.tags
        orm_place.address = place.address
        orm_place.source = place.source
        orm_place.is_active = place.is_active
        orm_place.updated_at = place.updated_at
        await self._session.flush()
        await self._session.refresh(orm_place)
        return orm_place.to_domain()

    async def delete(self, place_id: PlaceId) -> None:
        """Удаляет место."""
        stmt = select(PlaceORM).where(place_table.c.id == place_id.value)
        result = await self._session.execute(stmt)
        orm_place = result.scalar_one_or_none()
        if orm_place:
            await self._session.delete(orm_place)


__all__ = [
    "SQLAlchemyPlaceRepository",
]
