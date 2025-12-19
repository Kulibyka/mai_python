from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from app.config import Settings
from app.handlers import router
from app.services import LlmSummaryService
from app.storage import JsonStorage


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    settings = Settings.from_env()

    storage = JsonStorage(settings.data_dir)
    storage.ensure_seed_data()

    bot = Bot(token=settings.bot_token)
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(router)

    llm_service = LlmSummaryService()

    dispatcher["storage"] = storage
    dispatcher["llm"] = llm_service
    dispatcher["admin_ids"] = settings.admin_ids

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
