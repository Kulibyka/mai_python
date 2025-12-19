from __future__ import annotations

import random
from dataclasses import dataclass

from app.models import Place, Review


@dataclass
class SearchFilters:
    category: str | None = None
    price_level: str | None = None
    min_rating: float | None = None
    query: str | None = None


class RecommendationService:
    def filter_places(self, places: list[Place], filters: SearchFilters) -> list[Place]:
        results = [place for place in places if place.status == "approved"]
        if filters.category and filters.category != "Любая":
            results = [place for place in results if place.category == filters.category]
        if filters.price_level and filters.price_level != "Любой":
            results = [place for place in results if place.price_level == filters.price_level]
        if filters.min_rating is not None:
            results = [place for place in results if place.rating >= filters.min_rating]
        if filters.query:
            query_lower = filters.query.lower()
            results = [
                place
                for place in results
                if query_lower in place.name.lower()
                or query_lower in place.description.lower()
                or query_lower in place.address.lower()
            ]
        return sorted(results, key=lambda place: place.rating, reverse=True)

    def random_place(self, places: list[Place]) -> Place | None:
        approved = [place for place in places if place.status == "approved"]
        if not approved:
            return None
        return random.choice(approved)


class LlmSummaryService:
    def __init__(self) -> None:
        self._cache: dict[int, str] = {}

    def summarize(self, place: Place, reviews: list[Review]) -> str:
        if place.id in self._cache:
            return self._cache[place.id]
        if not reviews:
            summary = (
                "Пока мало отзывов. Место выглядит перспективно, "
                "поэтому стоит проверить лично!"
            )
        else:
            positives = [review for review in reviews if review.rating >= 4.0]
            if positives:
                summary = (
                    "Пользователи отмечают приятную атмосферу и хорошее обслуживание."
                )
            else:
                summary = (
                    "Отзывы смешанные: есть что улучшить, но место вызывает интерес."
                )
        self._cache[place.id] = summary
        return summary
