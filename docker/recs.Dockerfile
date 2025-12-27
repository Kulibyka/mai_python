FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git \
    && rm -rf /var/lib/apt/lists/*

COPY src/recs/pyproject.toml src/recs/poetry.lock ./

RUN pip install "poetry==2.1.2" \
    && poetry install --no-root


COPY src/recs /app

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "lib.main.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
