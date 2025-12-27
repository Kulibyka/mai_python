"""Контейнер зависимостей для приложения."""

import contextlib
import logging

from dishka import AsyncContainer, make_async_container

import lib.utils.logging as logging_utils
from lib.main.ioc.providers import (
    DatabaseProvider,
    GatewayProvider,
    InfrastructureProvider,
    InteractorProvider,
    QdrantProvider,
    ServiceProvider,
    SettingsProvider,
)
from lib.main.settings import Settings

logger = logging.getLogger(__name__)


def setup_container() -> AsyncContainer:
    """
    Создает и настраивает контейнер зависимостей.

    :return: Настроенный контейнер зависимостей
    """
    return make_async_container(
        SettingsProvider(),
        DatabaseProvider(),
        QdrantProvider(),
        GatewayProvider(),
        InfrastructureProvider(),
        ServiceProvider(),
        InteractorProvider(),
    )


async def initialize_app(settings: Settings) -> None:
    """
    Инициализирует приложение: настраивает логирование.

    :param settings: Настройки приложения
    """
    logging_config = logging_utils.create_config(
        log_level=settings.log.level,
        log_format=settings.log.format,
        loggers=settings.log.loggers,
    )
    logging_utils.initialize_logging(logging_config)
    logger.info("Приложение инициализировано")


@contextlib.asynccontextmanager
async def create_app_context():
    """
    Создает контекст приложения с контейнером зависимостей.

    :yield: Контейнер зависимостей
    """
    container = setup_container()
    settings = await container.get(Settings)

    await initialize_app(settings)

    try:
        yield container
    finally:
        await container.close()


__all__ = [
    "SettingsProvider",
    "create_app_context",
    "initialize_app",
    "setup_container",
]
