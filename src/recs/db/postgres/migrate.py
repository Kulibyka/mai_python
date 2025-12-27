"""
Скрипт для управления миграциями базы данных через Alembic.

Предоставляет CLI интерфейс для выполнения команд миграций:
upgrade, downgrade, revision, current, history.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from dotenv import load_dotenv


def _load_env() -> None:
    """
    Загружает переменные окружения из .env.
    Ищем .env:
      1) рядом с migrate.py (src/db/postgres/.env)
      2) в корне репозитория (../../.. относительно migrate.py)
    """
    here = Path(__file__).resolve().parent

    candidates = [
        here / ".env",
        here.parents[2] / ".env",  # src/db/postgres -> src -> repo root (обычно)
        here.parents[3] / ".env",  # запасной вариант, если структура другая
    ]

    for p in candidates:
        if p.exists():
            load_dotenv(dotenv_path=p, override=False)
            return

    # Если .env не найден — не ошибка, просто рассчитываем на реальные env vars
    load_dotenv(override=False)


def _alembic_cfg() -> Config:
    here = Path(__file__).resolve().parent
    alembic_ini = here / "alembic.ini"

    cfg = Config(str(alembic_ini))

    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError(
            "Не задана переменная окружения DATABASE_URL.\nДобавь её в .env или export в окружение",
        )

    cfg.set_main_option("sqlalchemy.url", dsn)
    cfg.set_main_option("script_location", str(here / "migrations"))
    return cfg


def main(argv: list[str]) -> int:  # noqa: C901, PLR0911
    """
    Главная функция CLI для управления миграциями.

    :param argv: Список аргументов командной строки
    :return: Код возврата (0 - успех, 2 - ошибка)
    """
    _load_env()
    cfg = _alembic_cfg()

    if len(argv) < 2:  # noqa: PLR2004
        print(  # noqa: T201
            "Usage:\n"
            "  python migrate.py upgrade [revision]\n"
            "  python migrate.py downgrade <revision>\n"
            '  python migrate.py revision -m "message" [--autogenerate]\n'
            "  python migrate.py current\n"
            "  python migrate.py history\n",
        )
        return 2

    cmd = argv[1]
    args = argv[2:]

    if cmd == "upgrade":
        rev = args[0] if args else "head"
        command.upgrade(cfg, rev)
        return 0

    if cmd == "downgrade":
        if not args:
            print("downgrade требует revision, например: downgrade -1 или downgrade base")  # noqa: T201
            return 2
        command.downgrade(cfg, args[0])
        return 0

    if cmd == "revision":
        # Поддержим:
        #  python migrate.py revision -m "init schema"
        #  python migrate.py revision -m "add docs" --autogenerate
        #  python migrate.py revision -m "init schema" --sql
        autogen = "--autogenerate" in args
        sql = "--sql" in args

        if autogen and sql:
            raise RuntimeError("Нельзя одновременно использовать --autogenerate и --sql")

        # достаём message
        msg = None
        if "-m" in args:
            i = args.index("-m")
            msg = args[i + 1]
        elif "--message" in args:
            i = args.index("--message")
            msg = args[i + 1]
        else:
            raise RuntimeError('Для revision нужно передать -m "message"')

        command.revision(cfg, message=msg, autogenerate=autogen, sql=sql)
        return 0

    if cmd == "current":
        command.current(cfg, verbose=True)
        return 0

    if cmd == "history":
        command.history(cfg, verbose=True)
        return 0

    print(f"Unknown command: {cmd}")  # noqa: T201
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
