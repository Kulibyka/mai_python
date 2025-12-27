"""
API версии 1.0.

Содержит endpoints, схемы данных и маршрутизацию
для первой версии REST API приложения.
"""

from fastapi import APIRouter

from .routers import place_router

api_router = APIRouter(prefix="/v1")
api_router.include_router(place_router)

__all__ = [
    "api_router",
]
