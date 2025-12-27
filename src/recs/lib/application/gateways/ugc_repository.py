"""Интерфейс репозитория пользовательского контента."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from lib.domain.entities.ugc import UGC
from lib.domain.enums import UgcKind
from lib.domain.value_objects import PlaceId, UserId


class IUGCRepository(ABC):
    """Интерфейс репозитория для работы с пользовательским контентом."""

    @abstractmethod
    async def get_by_id(self, ugc_id: UUID) -> UGC | None:
        """
        Получает UGC по идентификатору.

        :param ugc_id: Идентификатор UGC
        :return: UGC или None, если не найден
        """
        ...

    @abstractmethod
    async def get_by_user_and_place(
        self,
        user_id: UserId,
        place_id: PlaceId,
        kind: UgcKind | None = None,
    ) -> Sequence[UGC]:
        """
        Получает UGC по пользователю и месту.

        :param user_id: Идентификатор пользователя
        :param place_id: Идентификатор места
        :param kind: Тип UGC (опционально)
        :return: Список UGC
        """
        ...

    @abstractmethod
    async def get_by_place(
        self,
        place_id: PlaceId,
        kind: UgcKind | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Sequence[UGC]:
        """
        Получает UGC по месту.

        :param place_id: Идентификатор места
        :param kind: Тип UGC (опционально)
        :param limit: Максимальное количество результатов
        :param offset: Смещение для пагинации
        :return: Список UGC
        """
        ...

    @abstractmethod
    async def get_by_user(
        self,
        user_id: UserId,
        kind: UgcKind | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Sequence[UGC]:
        """
        Получает UGC по пользователю.

        :param user_id: Идентификатор пользователя
        :param kind: Тип UGC (опционально)
        :param limit: Максимальное количество результатов
        :param offset: Смещение для пагинации
        :return: Список UGC
        """
        ...

    @abstractmethod
    async def create(self, ugc: UGC) -> UGC:
        """
        Создает новый UGC.

        :param ugc: UGC для создания
        :return: Созданный UGC
        """
        ...

    @abstractmethod
    async def update(self, ugc: UGC) -> UGC:
        """
        Обновляет существующий UGC.

        :param ugc: UGC для обновления
        :return: Обновленный UGC
        """
        ...

    @abstractmethod
    async def delete(self, ugc_id: UUID) -> None:
        """
        Удаляет UGC (мягкое удаление через is_deleted).

        :param ugc_id: Идентификатор UGC для удаления
        """
        ...


__all__ = [
    "IUGCRepository",
]
