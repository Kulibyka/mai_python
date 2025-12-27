# mai_python

Телеграм-бот для рекомендаций мест отдыха и развлечений.

## Быстрый старт

1. Создайте `.env` по примеру `.env.example` и добавьте токен бота. При необходимости укажите `API_BASE_URL` для HTTP‑сервиса мест (по умолчанию — `http://localhost:8000`).
2. Установите зависимости:

```bash
python -m venv .venv
.venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

3. Запустите бота:

```bash
python bot.py
```

Убедитесь, что сервис рекомендаций запущен и доступен по адресу из `API_BASE_URL`.

## Запуск в Docker

1. Скопируйте пример окружения и заполните токен:

```bash
cp tg/.env.example tg/.env
```

2. Запустите все сервисы (Postgres, Qdrant, API и бота) одной командой:

```bash
docker compose up --build
```

По умолчанию API будет доступен на http://localhost:8000/v1, а бот возьмет этот адрес из `API_BASE_URL`.
