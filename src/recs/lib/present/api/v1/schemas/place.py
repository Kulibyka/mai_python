"""Схемы для работы с местами."""

from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class PlaceCreateRequest(BaseModel):
    """Схема запроса для создания места."""

    osm_id: str = Field(..., description="OSM идентификатор места")
    osm_type: str | None = Field(None, description="Тип OSM объекта")
    name: str | None = Field(None, description="Название места")
    category_key: str | None = Field(None, description="Ключ категории")
    category_value: str | None = Field(None, description="Значение категории")
    latitude: Decimal | None = Field(None, description="Широта")
    longitude: Decimal | None = Field(None, description="Долгота")
    tags: dict[str, Any] = Field(default_factory=dict, description="Теги места")
    address: dict[str, Any] = Field(default_factory=dict, description="Адрес места")
    source: dict[str, Any] = Field(default_factory=dict, description="Источник данных")
    is_active: bool = Field(default=True, description="Активно ли место")


class PlaceUpdateRequest(BaseModel):
    """Схема запроса для обновления места."""

    osm_type: str | None = Field(None, description="Тип OSM объекта")
    name: str | None = Field(None, description="Название места")
    category_key: str | None = Field(None, description="Ключ категории")
    category_value: str | None = Field(None, description="Значение категории")
    latitude: Decimal | None = Field(None, description="Широта")
    longitude: Decimal | None = Field(None, description="Долгота")
    tags: dict[str, Any] | None = Field(None, description="Теги места")
    address: dict[str, Any] | None = Field(None, description="Адрес места")
    source: dict[str, Any] | None = Field(None, description="Источник данных")
    is_active: bool | None = Field(None, description="Активно ли место")


class PlaceSearchRequest(BaseModel):
    """Схема запроса для поиска мест."""

    query: str | None = Field(None, description="Текст запроса для векторного поиска (естественный язык)")
    category_key: str | None = Field(None, description="Ключ категории")
    category_value: str | None = Field(None, description="Значение категории")
    latitude: Decimal | None = Field(None, description="Широта для поиска по координатам")
    longitude: Decimal | None = Field(None, description="Долгота для поиска по координатам")
    radius_km: Decimal | None = Field(None, description="Радиус поиска в километрах")
    limit: int = Field(10, ge=1, le=100, description="Максимальное количество результатов")
    offset: int = Field(0, ge=0, description="Смещение для пагинации")
    score_threshold: float | None = Field(None, ge=0.0, le=1.0, description="Минимальный порог схожести")


class PlaceResponse(BaseModel):
    """Схема ответа с информацией о месте."""

    id: UUID
    osm_id: str
    osm_type: str | None
    name: str | None
    category_key: str | None
    category_value: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    tags: dict[str, Any]
    address: dict[str, Any]
    source: dict[str, Any]
    is_active: bool
    created_at: str
    updated_at: str


class PlaceSearchResultResponse(BaseModel):
    """Схема результата поиска места."""

    place: PlaceResponse
    score: float | None = Field(None, description="Score схожести (для векторного поиска)")


class PlaceSearchResponse(BaseModel):
    """Схема ответа с результатами поиска."""

    results: list[PlaceSearchResultResponse]
    total: int | None = Field(None, description="Общее количество результатов (если известно)")
    limit: int
    offset: int


__all__ = [
    "PlaceCreateRequest",
    "PlaceResponse",
    "PlaceSearchRequest",
    "PlaceSearchResponse",
    "PlaceSearchResultResponse",
    "PlaceUpdateRequest",
]
