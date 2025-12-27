"""Реализация репозитория пользователей."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lib.application.gateways.user_repository import IUserRepository
from lib.domain.entities.user import User
from lib.domain.value_objects import Email, UserId, Username
from lib.infra.db.orm_models.user import UserORM, user_table


class SQLAlchemyUserRepository(IUserRepository):
    """Реализация репозитория пользователей на SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализирует репозиторий с сессией SQLAlchemy.

        :param session: Асинхронная сессия SQLAlchemy
        """
        self._session = session

    async def get_by_id(self, user_id: UserId) -> User | None:
        """Получает пользователя по идентификатору."""
        stmt = select(UserORM).where(user_table.c.id == user_id.value)
        result = await self._session.execute(stmt)
        orm_user = result.scalar_one_or_none()
        return orm_user.to_domain() if orm_user else None

    async def get_by_email(self, email: Email) -> User | None:
        """Получает пользователя по email."""
        stmt = select(UserORM).where(user_table.c.email == email.value)
        result = await self._session.execute(stmt)
        orm_user = result.scalar_one_or_none()
        return orm_user.to_domain() if orm_user else None

    async def get_by_username(self, username: Username) -> User | None:
        """Получает пользователя по имени пользователя."""
        stmt = select(UserORM).where(user_table.c.username == username.value)
        result = await self._session.execute(stmt)
        orm_user = result.scalar_one_or_none()
        return orm_user.to_domain() if orm_user else None

    async def list_all(self, limit: int | None = None, offset: int = 0) -> list[User]:
        """Получает список пользователей с пагинацией."""
        stmt = select(UserORM).offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self._session.execute(stmt)
        orm_users = result.scalars().all()
        return [orm_user.to_domain() for orm_user in orm_users]

    async def create(self, user: User) -> User:
        """Создает нового пользователя."""
        orm_user = UserORM.from_domain(user)
        self._session.add(orm_user)
        await self._session.flush()
        await self._session.refresh(orm_user)
        return orm_user.to_domain()

    async def update(self, user: User) -> User:
        """Обновляет существующего пользователя."""
        stmt = select(UserORM).where(user_table.c.id == user.id.value)
        result = await self._session.execute(stmt)
        orm_user = result.scalar_one()
        orm_user.email = user.email.value if user.email else None
        orm_user.username = user.username.value if user.username else None
        orm_user.password_hash = user.password_hash
        orm_user.is_active = user.is_active
        orm_user.is_verified = user.is_verified
        orm_user.profile = user.profile
        orm_user.preferences = user.preferences
        orm_user.meta = user.meta
        orm_user.last_login_at = user.last_login_at
        orm_user.updated_at = user.updated_at
        await self._session.flush()
        await self._session.refresh(orm_user)
        return orm_user.to_domain()

    async def delete(self, user_id: UserId) -> None:
        """Удаляет пользователя."""
        stmt = select(UserORM).where(user_table.c.id == user_id.value)
        result = await self._session.execute(stmt)
        orm_user = result.scalar_one_or_none()
        if orm_user:
            await self._session.delete(orm_user)


__all__ = [
    "SQLAlchemyUserRepository",
]
