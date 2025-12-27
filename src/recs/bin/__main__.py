"""Стандартный запуск приложения"""

import asyncio
import logging
import os
import sys

from lib.main.ioc import create_app_context
from lib.main.settings import Settings

logger = logging.getLogger(__name__)


async def run() -> None:
    """Запуск приложения"""
    async with create_app_context() as container:
        settings = await container.get(Settings)
        logger.info("Приложение запущено")
        logger.debug("Настройки: %s", settings)


def main() -> None:
    """Запуск приложения и обработка ошибок"""

    try:
        asyncio.run(run())
        sys.exit(os.EX_OK)
    except SystemExit:
        sys.exit(os.EX_OK)
    # except _errors.ApplicationError:
    #     sys.exit(70)
    except KeyboardInterrupt:
        logger.info("Exited with keyboard interruption")
        sys.exit(os.EX_OK)
    except BaseException:
        logger.exception("Unexpected error occurred")
        sys.exit(70)


if __name__ == "__main__":
    main()
