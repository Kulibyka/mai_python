"""
Скрипт для управления миграциями Qdrant.

Предоставляет CLI интерфейс для выполнения команд миграций:
upgrade, downgrade, current, history.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from qdrant_client import QdrantClient


def _load_env() -> None:
    """
    Загружает переменные окружения из .env.

    Ищем .env:
      1) рядом с migrate.py (src/db/qdrant/.env)
      2) в корне репозитория (../../.. относительно migrate.py)
    """
    here = Path(__file__).resolve().parent

    candidates = [
        here / ".env",
        here.parents[2] / ".env",  # src/db/qdrant -> src -> repo root (обычно)
        here.parents[3] / ".env",  # запасной вариант, если структура другая
    ]

    for p in candidates:
        if p.exists():
            load_dotenv(dotenv_path=p, override=False)
            return

    # Если .env не найден — не ошибка, просто рассчитываем на реальные env vars
    load_dotenv(override=False)


def _get_qdrant_client() -> QdrantClient:
    """
    Создает клиент Qdrant из переменных окружения.

    :return: Клиент Qdrant
    """
    url = os.environ.get("QDRANT_URL", "http://localhost:6333")
    api_key = os.environ.get("QDRANT_API_KEY")

    if api_key:
        return QdrantClient(url=url, api_key=api_key)
    return QdrantClient(url=url)


def _get_migrations() -> list[tuple[str, Path]]:
    """
    Получает список миграций в порядке их применения.

    :return: Список кортежей (revision, path)
    """
    import importlib.util

    here = Path(__file__).resolve().parent
    versions_dir = here / "migrations" / "versions"

    if not versions_dir.exists():
        return []

    migrations: list[tuple[str, Path]] = []
    for file in sorted(versions_dir.glob("*.py")):
        if file.name == "__init__.py":
            continue

        # Импортируем модуль миграции
        spec = importlib.util.spec_from_file_location("migration", file)
        if spec is None or spec.loader is None:
            continue

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "revision"):
            revision: str = module.revision
            migrations.append((revision, file))

    # Сортируем по revision
    migrations.sort(key=lambda x: x[0])
    return migrations


def _get_applied_migrations(client: QdrantClient) -> set[str]:
    """
    Получает список примененных миграций из Qdrant.

    В Qdrant нет встроенной системы отслеживания миграций,
    поэтому используем коллекцию для хранения информации о миграциях.

    :param client: Клиент Qdrant
    :return: Множество примененных revision
    """
    # TODO: Реализовать хранение информации о миграциях в Qdrant
    # Пока возвращаем пустое множество
    return set()


def upgrade(target_revision: str | None = None) -> None:
    """
    Применяет миграции до указанной версии (или до последней).

    :param target_revision: Целевая версия миграции (None = последняя)
    """
    _load_env()
    client = _get_qdrant_client()
    migrations = _get_migrations()
    applied = _get_applied_migrations(client)

    if not migrations:
        print("Миграции не найдены")
        return

    # Определяем целевую версию
    if target_revision is None:
        target_revision = migrations[-1][0]

    # Применяем миграции
    for revision, path in migrations:
        if revision in applied:
            print(f"Миграция {revision} уже применена, пропускаем")
            continue

        if revision > target_revision:
            break

        print(f"Применяем миграцию {revision}...")

        # Импортируем и выполняем миграцию
        import importlib.util

        spec = importlib.util.spec_from_file_location("migration", path)
        if spec is None or spec.loader is None:
            print(f"Ошибка загрузки миграции {revision}")
            continue

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        try:
            module.upgrade(client)
            print(f"Миграция {revision} успешно применена")
            # TODO: Сохранить информацию о примененной миграции
        except Exception as e:
            print(f"Ошибка применения миграции {revision}: {e}")
            raise


def downgrade(target_revision: str | None = None) -> None:
    """
    Откатывает миграции до указанной версии.

    :param target_revision: Целевая версия миграции (None = откатить все)
    """
    _load_env()
    client = _get_qdrant_client()
    migrations = _get_migrations()
    applied = _get_applied_migrations(client)

    if not migrations:
        print("Миграции не найдены")
        return

    # Применяем миграции в обратном порядке
    for revision, path in reversed(migrations):
        if revision not in applied:
            continue

        if target_revision is not None and revision <= target_revision:
            break

        print(f"Откатываем миграцию {revision}...")

        # Импортируем и выполняем откат
        import importlib.util

        spec = importlib.util.spec_from_file_location("migration", path)
        if spec is None or spec.loader is None:
            print(f"Ошибка загрузки миграции {revision}")
            continue

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        try:
            module.downgrade(client)
            print(f"Миграция {revision} успешно откачена")
            # TODO: Удалить информацию о примененной миграции
        except Exception as e:
            print(f"Ошибка отката миграции {revision}: {e}")
            raise


def current() -> None:
    """Показывает текущую версию миграции."""
    _load_env()
    client = _get_qdrant_client()
    applied = _get_applied_migrations(client)

    if not applied:
        print("Нет примененных миграций")
        return

    # Показываем последнюю примененную миграцию
    last_revision = max(applied)
    print(f"Текущая версия: {last_revision}")


def history() -> None:
    """Показывает историю миграций."""
    migrations = _get_migrations()
    applied: set[str] = set()  # TODO: Получить из Qdrant

    if not migrations:
        print("Миграции не найдены")
        return

    print("История миграций:")
    for revision, path in migrations:
        status = "✓" if revision in applied else " "
        print(f"  {status} {revision} - {path.name}")


def main() -> None:
    """Главная функция CLI."""
    if len(sys.argv) < 2:
        print("Использование: python migrate.py <command> [args]")
        print("Команды: upgrade [revision], downgrade [revision], current, history")
        sys.exit(1)

    command = sys.argv[1]

    if command == "upgrade":
        target = sys.argv[2] if len(sys.argv) > 2 else None
        upgrade(target)
    elif command == "downgrade":
        target = sys.argv[2] if len(sys.argv) > 2 else None
        downgrade(target)
    elif command == "current":
        current()
    elif command == "history":
        history()
    else:
        print(f"Неизвестная команда: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()


__all__ = [
    "current",
    "downgrade",
    "history",
    "main",
    "upgrade",
]
