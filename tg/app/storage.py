from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tg.app.models import Place, Review, UserProfile, utc_now


class JsonStorage:
    def __init__(self, data_dir: str) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._places_path = self.data_dir / "places.json"
        self._reviews_path = self.data_dir / "reviews.json"
        self._profiles_path = self.data_dir / "profiles.json"
        self._likes_path = self.data_dir / "likes.json"

        self._places: dict[int, Place] = {}
        self._reviews: dict[int, Review] = {}
        self._profiles: dict[int, UserProfile] = {}
        self._likes: dict[str, list[int]] = {}

        self._load_all()

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(self, path: Path, data: Any) -> None:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_all(self) -> None:
        places_raw = self._read_json(self._places_path, [])
        self._places = {item["id"]: Place.from_dict(item) for item in places_raw}

        reviews_raw = self._read_json(self._reviews_path, [])
        self._reviews = {item["id"]: Review.from_dict(item) for item in reviews_raw}

        profiles_raw = self._read_json(self._profiles_path, [])
        self._profiles = {
            item["user_id"]: UserProfile.from_dict(item) for item in profiles_raw
        }

        self._likes = self._read_json(self._likes_path, {})

    def _save_all(self) -> None:
        self._write_json(
            self._places_path, [place.to_dict() for place in self._places.values()]
        )
        self._write_json(
            self._reviews_path,
            [review.to_dict() for review in self._reviews.values()],
        )
        self._write_json(
            self._profiles_path,
            [profile.to_dict() for profile in self._profiles.values()],
        )
        self._write_json(self._likes_path, self._likes)

    def ensure_seed_data(self) -> None:
        if self._places:
            return
        sample_places = [
            Place(
                id=1,
                name="Кофейня Сосны",
                category="Кофейни",
                address="ул. Лесная, 10",
                description="Спокойная кофейня с авторскими десертами.",
                price_level="Средний",
                rating=4.6,
                status="approved",
                created_by=0,
                created_at=utc_now(),
                contacts="https://example.com/coffee",
            ),
            Place(
                id=2,
                name="Парк Зеленый берег",
                category="Парки",
                address="набережная, 5",
                description="Большой парк для прогулок и пикников.",
                price_level="Бюджетный",
                rating=4.4,
                status="approved",
                created_by=0,
                created_at=utc_now(),
            ),
            Place(
                id=3,
                name="Музей современного искусства",
                category="Музеи",
                address="пр. Центральный, 25",
                description="Выставки локальных художников.",
                price_level="Средний",
                rating=4.7,
                status="approved",
                created_by=0,
                created_at=utc_now(),
                contacts="https://example.com/museum",
            ),
        ]
        self._places = {place.id: place for place in sample_places}
        self._save_all()

    def next_place_id(self) -> int:
        return max(self._places.keys(), default=0) + 1

    def next_review_id(self) -> int:
        return max(self._reviews.keys(), default=0) + 1

    def list_places(self, status: str | None = None) -> list[Place]:
        places = list(self._places.values())
        if status:
            places = [place for place in places if place.status == status]
        return places

    def get_place(self, place_id: int) -> Place | None:
        return self._places.get(place_id)

    def add_place(self, place: Place) -> None:
        self._places[place.id] = place
        self._save_all()

    def update_place(self, place: Place) -> None:
        self._places[place.id] = place
        self._save_all()

    def list_reviews(self, place_id: int, status: str | None = None) -> list[Review]:
        reviews = [review for review in self._reviews.values() if review.place_id == place_id]
        if status:
            reviews = [review for review in reviews if review.status == status]
        return reviews

    def add_review(self, review: Review) -> None:
        self._reviews[review.id] = review
        self._save_all()

    def get_profile(self, user_id: int) -> UserProfile:
        profile = self._profiles.get(user_id)
        if profile is None:
            profile = UserProfile(user_id=user_id)
            self._profiles[user_id] = profile
            self._save_all()
        return profile

    def toggle_favorite(self, user_id: int, place_id: int) -> bool:
        profile = self.get_profile(user_id)
        if place_id in profile.favorites:
            profile.favorites.remove(place_id)
            is_favorite = False
        else:
            profile.favorites.add(place_id)
            is_favorite = True
        self._profiles[user_id] = profile
        self._save_all()
        return is_favorite

    def list_favorites(self, user_id: int) -> list[Place]:
        profile = self.get_profile(user_id)
        return [place for place_id in profile.favorites if (place := self.get_place(place_id))]

    def list_user_places(self, user_id: int) -> list[Place]:
        return [place for place in self._places.values() if place.created_by == user_id]

    def record_like(self, user_id: int, place_id: int, value: int) -> None:
        key = str(user_id)
        self._likes.setdefault(key, [])
        self._likes[key].append(value)
        self._save_all()
