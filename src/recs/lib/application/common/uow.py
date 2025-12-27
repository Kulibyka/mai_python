"""
Абстракция UoW
"""

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self


class IUnitOfWork(ABC):
    """
    Контракт для всех реализаций UoW.
    """

    @abstractmethod
    async def __aenter__(self) -> Self:
        """
        Использование UoW в блоках `with`.
        """
        ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Авто-коммит или откат транзакции при выходе из `with`.
        """
        ...

    @abstractmethod
    async def commit(self) -> None:
        """
        Подтверждение транзакции.
        """
        ...

    @abstractmethod
    async def rollback(self) -> None:
        """
        Откат транзакции.
        """
        ...
