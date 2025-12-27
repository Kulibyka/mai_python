"""Зависимости для FastAPI эндпоинтов."""

from typing import Annotated

from dishka import AsyncContainer
from fastapi import Depends, Request

from lib.application.interactors.place_interactor import (
    CreatePlaceInteractor,
    DeletePlaceInteractor,
    GetPlaceInteractor,
    SearchPlacesInteractor,
    UpdatePlaceInteractor,
)


def get_container(request: Request) -> AsyncContainer:
    """
    Получает контейнер зависимостей из состояния запроса.

    :param request: FastAPI request объект
    :return: Контейнер зависимостей
    """
    return request.state.container


async def get_create_place_interactor(
    container: Annotated[AsyncContainer, Depends(get_container)],
) -> CreatePlaceInteractor:
    """
    Получает интерактор для создания места.

    :param container: Контейнер зависимостей
    :return: Интерактор для создания места
    """
    return await container.get(CreatePlaceInteractor)


async def get_place_interactor(
    container: Annotated[AsyncContainer, Depends(get_container)],
) -> GetPlaceInteractor:
    """
    Получает интерактор для получения места.

    :param container: Контейнер зависимостей
    :return: Интерактор для получения места
    """
    return await container.get(GetPlaceInteractor)


async def get_update_place_interactor(
    container: Annotated[AsyncContainer, Depends(get_container)],
) -> UpdatePlaceInteractor:
    """
    Получает интерактор для обновления места.

    :param container: Контейнер зависимостей
    :return: Интерактор для обновления места
    """
    return await container.get(UpdatePlaceInteractor)


async def get_delete_place_interactor(
    container: Annotated[AsyncContainer, Depends(get_container)],
) -> DeletePlaceInteractor:
    """
    Получает интерактор для удаления места.

    :param container: Контейнер зависимостей
    :return: Интерактор для удаления места
    """
    return await container.get(DeletePlaceInteractor)


async def get_search_places_interactor(
    container: Annotated[AsyncContainer, Depends(get_container)],
) -> SearchPlacesInteractor:
    """
    Получает интерактор для поиска мест.

    :param container: Контейнер зависимостей
    :return: Интерактор для поиска мест
    """
    return await container.get(SearchPlacesInteractor)


__all__ = [
    "get_container",
    "get_create_place_interactor",
    "get_delete_place_interactor",
    "get_place_interactor",
    "get_search_places_interactor",
    "get_update_place_interactor",
]
