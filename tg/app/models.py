from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Mapping


@dataclass
class Place:
    id: str
    name: str
    category: str | None = None
    address: str | None = None
    description: str | None = None
    price_level: str | None = None
    rating: float | None = None
    status: str | None = None
    created_by: int | None = None
    created_at: str | None = None
    contacts: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    score: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Place":
        data = data.copy()
        data["id"] = str(data["id"])
        return cls(**data)

    @classmethod
    def from_api(cls, data: Mapping[str, Any]) -> "Place":
        place_data = data.get("place", data)
        address = cls._format_address(place_data.get("address", {}))
        tags: Mapping[str, Any] = place_data.get("tags", {})
        description = cls._build_description(tags)
        latitude = cls._to_float(place_data.get("latitude"))
        longitude = cls._to_float(place_data.get("longitude"))
        score = data.get("score")

        return cls(
            id=str(place_data["id"]),
            name=place_data.get("name") or "Без названия",
            category=place_data.get("category_value") or place_data.get("category_key"),
            address=address,
            description=description,
            price_level=None,
            rating=None,
            status="active" if place_data.get("is_active", True) else "inactive",
            created_by=None,
            created_at=place_data.get("created_at"),
            contacts=tags.get("contact:phone") or tags.get("phone"),
            latitude=latitude,
            longitude=longitude,
            score=score if isinstance(score, (int, float)) else None,
        )

    @staticmethod
    def _to_float(value: Any) -> float | None:
        if value is None:
            return None
        if isinstance(value, Decimal):
            return float(value)
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _format_address(address: Mapping[str, Any]) -> str | None:
        if not address:
            return None
        parts = []
        for key in ("road", "house_number", "city", "state", "country"):
            part = address.get(key)
            if part:
                parts.append(str(part))
        if parts:
            return ", ".join(parts)
        return address.get("display_name") or None

    @staticmethod
    def _build_description(tags: Mapping[str, Any]) -> str | None:
        if not tags:
            return None
        hints = []
        for key in ("amenity", "cuisine", "tourism", "leisure"):
            value = tags.get(key)
            if value:
                hints.append(str(value))
        return ", ".join(hints) or None


@dataclass
class Review:
    id: int
    place_id: int
    user_id: int
    rating: float
    text: str
    status: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Review":
        return cls(**data)


@dataclass
class UserProfile:
    user_id: int
    favorites: set[str] = field(default_factory=set)

    def to_dict(self) -> dict[str, Any]:
        return {"user_id": self.user_id, "favorites": list(self.favorites)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserProfile":
        favorites = {str(item) for item in data.get("favorites", [])}
        return cls(user_id=data["user_id"], favorites=favorites)


def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"
