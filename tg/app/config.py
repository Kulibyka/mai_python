from __future__ import annotations

import os
from dataclasses import dataclass


def _split_ints(value: str | None) -> set[int]:
    if not value:
        return set()
    return {int(item.strip()) for item in value.split(",") if item.strip().isdigit()}


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_ids: set[int]
    data_dir: str
    api_base_url: str


    @classmethod
    def from_env(cls) -> "Settings":
        token = os.getenv("BOT_TOKEN", "")
        if not token:
            raise RuntimeError("BOT_TOKEN is required")
        return cls(
            bot_token=token,
            admin_ids=_split_ints(os.getenv("ADMIN_IDS")),
            data_dir=os.getenv("DATA_DIR", "data"),
            api_base_url=os.getenv("API_BASE_URL", "http://localhost:8000/v1"),
        )
