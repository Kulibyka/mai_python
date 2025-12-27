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
