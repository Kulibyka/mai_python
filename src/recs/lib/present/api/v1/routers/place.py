"""Роутер для работы с местами."""

from collections.abc import Sequence
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from lib.application.dto.place_dto import (
    PlaceCreateDTO,
    PlaceResponseDTO,
    PlaceSearchDTO,
    PlaceSearchResultDTO,
    PlaceUpdateDTO,
)
from lib.application.interactors.place_interactor import (
    CreatePlaceInteractor,
    DeletePlaceInteractor,
    GetPlaceInteractor,
    SearchPlacesInteractor,
    UpdatePlaceInteractor,
)
from lib.domain.value_objects import PlaceId
from lib.present.api.deps import (
    get_create_place_interactor,
    get_delete_place_interactor,
    get_place_interactor,
    get_search_places_interactor,
    get_update_place_interactor,
)
from lib.present.api.v1.schemas.place import (
    PlaceCreateRequest,
    PlaceResponse,
    PlaceSearchRequest,
    PlaceSearchResponse,
    PlaceSearchResultResponse,
    PlaceUpdateRequest,
)

router = APIRouter(prefix="/places", tags=["places"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_place(
    request: PlaceCreateRequest,
    interactor: Annotated[CreatePlaceInteractor, Depends(get_create_place_interactor)],
) -> PlaceResponse:
    """
    Создает новое место.

    :param request: Данные для создания места
    :param interactor: Интерактор для создания места
    :return: Созданное место
    """
    dto = PlaceCreateDTO(
        osm_id=request.osm_id,
        osm_type=request.osm_type,
        name=request.name,
        category_key=request.category_key,
        category_value=request.category_value,
        latitude=request.latitude,
        longitude=request.longitude,
        tags=request.tags,
        address=request.address,
        source=request.source,
        is_active=request.is_active,
    )

    result = await interactor.execute(dto)
    return _dto_to_response(result)


@router.get("/{place_id}")
async def get_place(
    place_id: UUID,
    interactor: Annotated[GetPlaceInteractor, Depends(get_place_interactor)],
) -> PlaceResponse:
    """
    Получает место по идентификатору.

    :param place_id: Идентификатор места
    :param interactor: Интерактор для получения места
    :return: Информация о месте
    """
    place_dto = await interactor.execute(PlaceId(value=place_id))
    if not place_dto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Place with id {place_id} not found",
        )

    return _dto_to_response(place_dto)


@router.put("/{place_id}")
async def update_place(
    place_id: UUID,
    request: PlaceUpdateRequest,
    interactor: Annotated[UpdatePlaceInteractor, Depends(get_update_place_interactor)],
) -> PlaceResponse:
    """
    Обновляет место.

    :param place_id: Идентификатор места
    :param request: Данные для обновления
    :param interactor: Интерактор для обновления места
    :return: Обновленное место
    """
    dto = PlaceUpdateDTO(
        osm_type=request.osm_type,
        name=request.name,
        category_key=request.category_key,
        category_value=request.category_value,
        latitude=request.latitude,
        longitude=request.longitude,
        tags=request.tags,
        address=request.address,
        source=request.source,
        is_active=request.is_active,
    )

    result = await interactor.execute(PlaceId(value=place_id), dto)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Place with id {place_id} not found",
        )

    return _dto_to_response(result)


@router.delete("/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_place(
    place_id: UUID,
    interactor: Annotated[DeletePlaceInteractor, Depends(get_delete_place_interactor)],
) -> None:
    """
    Удаляет место.

    :param place_id: Идентификатор места
    :param interactor: Интерактор для удаления места
    """
    deleted = await interactor.execute(PlaceId(value=place_id))
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Place with id {place_id} not found",
        )


@router.post("/search")
async def search_places(
    request: PlaceSearchRequest,
    interactor: Annotated[SearchPlacesInteractor, Depends(get_search_places_interactor)],
) -> PlaceSearchResponse:
    """
    Ищет места по различным критериям.

    Основной эндпоинт для поиска мест по естественному языку.
    Принимает текстовый запрос и возвращает релевантные места.

    :param request: Параметры поиска
    :param interactor: Интерактор для поиска мест
    :return: Результаты поиска
    """
    dto = PlaceSearchDTO(
        query=request.query,
        vector=None,  # Вектор генерируется автоматически из query
        category_key=request.category_key,
        category_value=request.category_value,
        latitude=request.latitude,
        longitude=request.longitude,
        radius_km=request.radius_km,
        limit=request.limit,
        offset=request.offset,
        score_threshold=request.score_threshold,
    )

    results = await interactor.execute(dto)
    return _search_results_to_response(results, request.limit, request.offset)


@router.get("")
async def search_places_get(  # noqa: PLR0913
    interactor: Annotated[
        SearchPlacesInteractor,
        Depends(get_search_places_interactor),
    ],
    query: str | None = None,
    category_key: str | None = None,
    category_value: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    radius_km: float | None = None,
    limit: int = 10,
    offset: int = 0,
    score_threshold: float | None = None,
) -> PlaceSearchResponse:
    """
    Ищет места по различным критериям (GET версия).

    Удобный эндпоинт для простых запросов через URL параметры.
    Основной эндпоинт для Telegram бота - принимает естественный текст в параметре query.

    :param query: Текст запроса для векторного поиска (естественный язык)
    :param category_key: Ключ категории
    :param category_value: Значение категории
    :param latitude: Широта для поиска по координатам
    :param longitude: Долгота для поиска по координатам
    :param radius_km: Радиус поиска в километрах
    :param limit: Максимальное количество результатов
    :param offset: Смещение для пагинации
    :param score_threshold: Минимальный порог схожести
    :param interactor: Интерактор для поиска мест
    :return: Результаты поиска
    """
    dto = PlaceSearchDTO(
        query=query,
        vector=None,
        category_key=category_key,
        category_value=category_value,
        latitude=Decimal(str(latitude)) if latitude is not None else None,
        longitude=Decimal(str(longitude)) if longitude is not None else None,
        radius_km=Decimal(str(radius_km)) if radius_km is not None else None,
        limit=limit,
        offset=offset,
        score_threshold=score_threshold,
    )

    results = await interactor.execute(dto)
    return _search_results_to_response(results, limit, offset)


def _dto_to_response(dto: PlaceResponseDTO) -> PlaceResponse:
    """
    Преобразует DTO в схему ответа.

    :param dto: DTO ответа
    :return: Схема ответа
    """
    return PlaceResponse(
        id=dto.id,
        osm_id=dto.osm_id,
        osm_type=dto.osm_type,
        name=dto.name,
        category_key=dto.category_key,
        category_value=dto.category_value,
        latitude=dto.latitude,
        longitude=dto.longitude,
        tags=dto.tags,
        address=dto.address,
        source=dto.source,
        is_active=dto.is_active,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


def _search_results_to_response(
    results: list[PlaceSearchResultDTO] | Sequence[PlaceSearchResultDTO],
    limit: int,
    offset: int,
) -> PlaceSearchResponse:
    """
    Преобразует результаты поиска в схему ответа.

    :param results: Результаты поиска
    :param limit: Лимит результатов
    :param offset: Смещение
    :return: Схема ответа с результатами
    """
    return PlaceSearchResponse(
        results=[
            PlaceSearchResultResponse(
                place=_dto_to_response(result.place),
                score=result.score,
            )
            for result in results
        ],
        total=None,  # TODO: Добавить подсчет общего количества при необходимости  # noqa: FIX002, TD002, TD003
        limit=limit,
        offset=offset,
    )


__all__ = [
    "router",
]
