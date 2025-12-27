"""Реализация репозитория пользовательского контента."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lib.application.gateways.ugc_repository import IUGCRepository
from lib.domain.entities.ugc import UGC
from lib.domain.enums import UgcKind
from lib.domain.value_objects import PlaceId, UserId
from lib.infra.db.orm_models.ugc import UGCORM, ugc_table


class SQLAlchemyUGCRepository(IUGCRepository):
    """Реализация репозитория пользовательского контента на SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализирует репозиторий с сессией SQLAlchemy.

        :param session: Асинхронная сессия SQLAlchemy
        """
        self._session = session

    async def get_by_id(self, ugc_id: UUID) -> UGC | None:
        """Получает UGC по идентификатору."""
        stmt = select(UGCORM).where(ugc_table.c.id == ugc_id)
        result = await self._session.execute(stmt)
        orm_ugc = result.scalar_one_or_none()
        return orm_ugc.to_domain() if orm_ugc else None

    async def get_by_user_and_place(
        self,
        user_id: UserId,
        place_id: PlaceId,
        kind: UgcKind | None = None,
    ) -> list[UGC]:
        """Получает UGC по пользователю и месту."""
        stmt = (
            select(UGCORM)
            .where(ugc_table.c.user_id == user_id.value)
            .where(ugc_table.c.place_id == place_id.value)
            .where(ugc_table.c.is_deleted == False)  # noqa: E712
        )
        if kind:
            stmt = stmt.where(ugc_table.c.kind == kind.value)
        result = await self._session.execute(stmt)
        orm_ugcs = result.scalars().all()
        return [orm_ugc.to_domain() for orm_ugc in orm_ugcs]

    async def get_by_place(
        self,
        place_id: PlaceId,
        kind: UgcKind | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[UGC]:
        """Получает UGC по месту."""
        stmt = (
            select(UGCORM)
            .where(ugc_table.c.place_id == place_id.value)
            .where(ugc_table.c.is_deleted == False)  # noqa: E712
            .order_by(ugc_table.c.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if kind:
            stmt = stmt.where(ugc_table.c.kind == kind.value)
        result = await self._session.execute(stmt)
        orm_ugcs = result.scalars().all()
        return [orm_ugc.to_domain() for orm_ugc in orm_ugcs]

    async def get_by_user(
        self,
        user_id: UserId,
        kind: UgcKind | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[UGC]:
        """Получает UGC по пользователю."""
        stmt = (
            select(UGCORM)
            .where(ugc_table.c.user_id == user_id.value)
            .where(ugc_table.c.is_deleted == False)  # noqa: E712
            .order_by(ugc_table.c.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if kind:
            stmt = stmt.where(ugc_table.c.kind == kind.value)
        result = await self._session.execute(stmt)
        orm_ugcs = result.scalars().all()
        return [orm_ugc.to_domain() for orm_ugc in orm_ugcs]

    async def create(self, ugc: UGC) -> UGC:
        """Создает новый UGC."""
        orm_ugc = UGCORM.from_domain(ugc)
        self._session.add(orm_ugc)
        await self._session.flush()
        await self._session.refresh(orm_ugc)
        return orm_ugc.to_domain()

    async def update(self, ugc: UGC) -> UGC:
        """Обновляет существующий UGC."""
        stmt = select(UGCORM).where(ugc_table.c.id == ugc.id)
        result = await self._session.execute(stmt)
        orm_ugc = result.scalar_one()
        orm_ugc.user_id = ugc.user_id.value
        orm_ugc.place_id = ugc.place_id.value
        orm_ugc.kind = ugc.kind.value
        orm_ugc.rating = int(ugc.rating.value) if ugc.rating else None
        orm_ugc.text = ugc.text
        orm_ugc.meta = ugc.meta
        orm_ugc.is_deleted = ugc.is_deleted
        orm_ugc.updated_at = ugc.updated_at
        await self._session.flush()
        await self._session.refresh(orm_ugc)
        return orm_ugc.to_domain()

    async def delete(self, ugc_id: UUID) -> None:
        """Удаляет UGC (мягкое удаление через is_deleted)."""
        stmt = select(UGCORM).where(ugc_table.c.id == ugc_id)
        result = await self._session.execute(stmt)
        orm_ugc = result.scalar_one_or_none()
        if orm_ugc:
            orm_ugc.is_deleted = True
            await self._session.flush()


__all__ = [
    "SQLAlchemyUGCRepository",
]
