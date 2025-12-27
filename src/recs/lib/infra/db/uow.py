"""
Реализация UoW
"""

import logging
from types import TracebackType
from typing import Self

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from lib.application.common.uow import IUnitOfWork

logger = logging.getLogger(__name__)


class SQLAlchemyUnitOfWork(IUnitOfWork):
    """
    Реализация UoW SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализируем UoW с открытой асинхронной сессией.

        :param session: Активная сеессия SQLAlchemy.
        """
        self.session = session

    async def __aenter__(self) -> Self:
        """
        Возвращает экземпляр UoW при входе в `async with`-блок.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Завершает транзакцию при выходе из `async with`-блока.

        :param exc_type: Тип возникшего исключения (если есть).
        :param exc_val: Экземпляр исключения (если есть).
        :param exc_tb: Трассировка стека (если есть).
        """
        if exc_type is not None:
            await self.session.rollback()
        else:
            try:
                await self.session.commit()
            except SQLAlchemyError:
                logger.exception("Ошибка SQLAlchemy, откат транзакции.")
                await self.session.rollback()
                raise

    async def commit(self) -> None:
        """
        Явно фиксирует транзакцию.
        """
        await self.session.commit()

    async def rollback(self) -> None:
        """
        Явно откатывает транзакцию.
        """
        await self.session.rollback()
