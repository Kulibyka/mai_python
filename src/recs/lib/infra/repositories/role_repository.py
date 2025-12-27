"""Реализация репозитория ролей."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lib.application.gateways.role_repository import IRoleRepository
from lib.domain.entities.role import Role
from lib.domain.enums import RoleName
from lib.domain.value_objects import RoleId
from lib.infra.db.orm_models.role import RoleORM, role_table


class SQLAlchemyRoleRepository(IRoleRepository):
    """Реализация репозитория ролей на SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализирует репозиторий с сессией SQLAlchemy.

        :param session: Асинхронная сессия SQLAlchemy
        """
        self._session = session

    async def get_by_id(self, role_id: RoleId) -> Role | None:
        """Получает роль по идентификатору."""
        stmt = select(RoleORM).where(role_table.c.id == role_id.value)
        result = await self._session.execute(stmt)
        orm_role = result.scalar_one_or_none()
        return orm_role.to_domain() if orm_role else None

    async def get_by_code(self, code: RoleName) -> Role | None:
        """Получает роль по коду."""
        stmt = select(RoleORM).where(role_table.c.code == code.value)
        result = await self._session.execute(stmt)
        orm_role = result.scalar_one_or_none()
        return orm_role.to_domain() if orm_role else None

    async def list_all(self) -> list[Role]:
        """Получает все роли."""
        stmt = select(RoleORM)
        result = await self._session.execute(stmt)
        orm_roles = result.scalars().all()
        return [orm_role.to_domain() for orm_role in orm_roles]

    async def create(self, role: Role) -> Role:
        """Создает новую роль."""
        orm_role = RoleORM.from_domain(role)
        self._session.add(orm_role)
        await self._session.flush()
        await self._session.refresh(orm_role)
        return orm_role.to_domain()

    async def update(self, role: Role) -> Role:
        """Обновляет существующую роль."""
        stmt = select(RoleORM).where(role_table.c.id == role.id.value)
        result = await self._session.execute(stmt)
        orm_role = result.scalar_one()
        orm_role.code = role.code.value
        orm_role.name = role.name
        orm_role.description = role.description
        orm_role.updated_at = role.updated_at
        await self._session.flush()
        await self._session.refresh(orm_role)
        return orm_role.to_domain()

    async def delete(self, role_id: RoleId) -> None:
        """Удаляет роль."""
        stmt = select(RoleORM).where(role_table.c.id == role_id.value)
        result = await self._session.execute(stmt)
        orm_role = result.scalar_one_or_none()
        if orm_role:
            await self._session.delete(orm_role)


__all__ = [
    "SQLAlchemyRoleRepository",
]
