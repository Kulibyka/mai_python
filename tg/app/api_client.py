from __future__ import annotations

import logging
from typing import Any

import httpx

from tg.app.models import Place

logger = logging.getLogger(__name__)


class PlacesApiClient:
    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def search_places(
        self,
        *,
        query: str | None = None,
        category: str | None = None,
        limit: int = 10,
    ) -> list[Place]:
        params: dict[str, Any] = {"limit": limit, "offset": 0}
        if query:
            params["query"] = query
        if category:
            params["category_value"] = category

        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
                response = await client.get("/places", params=params)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Не удалось получить места из API: %s", exc)
            return []

        payload = response.json()
        results: list[Place] = []
        for item in payload.get("results", []):
            try:
                results.append(Place.from_api(item))
            except Exception as exc:  # noqa: BLE001
                logger.debug("Пропущена запись из-за ошибки парсинга: %s", exc)
                continue
        return results

    async def get_place(self, place_id: str) -> Place | None:
        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
                response = await client.get(f"/places/{place_id}")
            if response.status_code == httpx.codes.NOT_FOUND:
                return None
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Не удалось получить место %s: %s", place_id, exc)
            return None

        try:
            return Place.from_api(response.json())
        except Exception as exc:  # noqa: BLE001
            logger.warning("Не удалось разобрать ответ API для %s: %s", place_id, exc)
            return None


__all__ = ["PlacesApiClient"]
