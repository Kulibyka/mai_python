from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Place:
    id: int
    name: str
    category: str
    address: str
    description: str
    price_level: str
    rating: float
    status: str
    created_by: int
    created_at: str
    contacts: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Place":
        return cls(**data)


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
    favorites: set[int] = field(default_factory=set)

    def to_dict(self) -> dict[str, Any]:
        return {"user_id": self.user_id, "favorites": list(self.favorites)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserProfile":
        return cls(user_id=data["user_id"], favorites=set(data.get("favorites", [])))


def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"
