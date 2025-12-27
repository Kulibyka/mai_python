"""Интерфейс репозитория ролей."""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from lib.domain.entities.role import Role
from lib.domain.enums import RoleName
from lib.domain.value_objects import RoleId


class IRoleRepository(ABC):
    """Интерфейс репозитория для работы с ролями."""

    @abstractmethod
    async def get_by_id(self, role_id: RoleId) -> Role | None:
        """
        Получает роль по идентификатору.

        :param role_id: Идентификатор роли
        :return: Роль или None, если не найдена
        """
        ...

    @abstractmethod
    async def get_by_code(self, code: RoleName) -> Role | None:
        """
        Получает роль по коду.

        :param code: Код роли
        :return: Роль или None, если не найдена
        """
        ...

    @abstractmethod
    async def list_all(self) -> Sequence[Role]:
        """
        Получает все роли.

        :return: Список всех ролей
        """
        ...

    @abstractmethod
    async def create(self, role: Role) -> Role:
        """
        Создает новую роль.

        :param role: Роль для создания
        :return: Созданная роль
        """
        ...

    @abstractmethod
    async def update(self, role: Role) -> Role:
        """
        Обновляет существующую роль.

        :param role: Роль для обновления
        :return: Обновленная роль
        """
        ...

    @abstractmethod
    async def delete(self, role_id: RoleId) -> None:
        """
        Удаляет роль.

        :param role_id: Идентификатор роли для удаления
        """
        ...


__all__ = [
    "IRoleRepository",
]
