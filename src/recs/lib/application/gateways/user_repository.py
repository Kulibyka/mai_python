"""Интерфейс репозитория пользователей."""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from lib.domain.entities.user import User
from lib.domain.value_objects import Email, UserId, Username


class IUserRepository(ABC):
    """Интерфейс репозитория для работы с пользователями."""

    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> User | None:
        """
        Получает пользователя по идентификатору.

        :param user_id: Идентификатор пользователя
        :return: Пользователь или None, если не найден
        """
        ...

    @abstractmethod
    async def get_by_email(self, email: Email) -> User | None:
        """
        Получает пользователя по email.

        :param email: Email пользователя
        :return: Пользователь или None, если не найден
        """
        ...

    @abstractmethod
    async def get_by_username(self, username: Username) -> User | None:
        """
        Получает пользователя по имени пользователя.

        :param username: Имя пользователя
        :return: Пользователь или None, если не найден
        """
        ...

    @abstractmethod
    async def list_all(self, limit: int | None = None, offset: int = 0) -> Sequence[User]:
        """
        Получает список пользователей с пагинацией.

        :param limit: Максимальное количество записей
        :param offset: Смещение для пагинации
        :return: Список пользователей
        """
        ...

    @abstractmethod
    async def create(self, user: User) -> User:
        """
        Создает нового пользователя.

        :param user: Пользователь для создания
        :return: Созданный пользователь
        """
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        """
        Обновляет существующего пользователя.

        :param user: Пользователь для обновления
        :return: Обновленный пользователь
        """
        ...

    @abstractmethod
    async def delete(self, user_id: UserId) -> None:
        """
        Удаляет пользователя.

        :param user_id: Идентификатор пользователя для удаления
        """
        ...


__all__ = [
    "IUserRepository",
]
