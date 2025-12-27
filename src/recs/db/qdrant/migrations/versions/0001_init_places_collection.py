"""
Создание коллекции places в Qdrant для векторного поиска мест.

Revision ID: 0001_init_places_collection
Revises:
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

revision = "0001_init_places_collection"
down_revision = None
branch_labels = None
depends_on = None

COLLECTION_NAME = "places"
VECTOR_SIZE = 384  # Размерность вектора для модели all-MiniLM-L6-v2
DISTANCE = Distance.COSINE


def upgrade(client: QdrantClient) -> None:
    """
    Создает коллекцию places в Qdrant для векторного поиска.

    Коллекция настроена для работы с эмбеддингами из модели all-MiniLM-L6-v2:
    - Размерность вектора: 384
    - Метрика расстояния: COSINE (для семантического поиска)
    - Payload будет содержать: name, category, lat, lon, tags

    :param client: Клиент Qdrant
    """
    # Проверяем, существует ли коллекция
    collections = client.get_collections().collections
    collection_exists = any(col.name == COLLECTION_NAME for col in collections)

    if collection_exists:
        # Если коллекция существует, пересоздаем её (recreate)
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=DISTANCE),
        )
    else:
        # Если коллекции нет, создаём новую
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=DISTANCE),
        )


def downgrade(client: QdrantClient) -> None:
    """
    Удаляет коллекцию places из Qdrant.

    :param client: Клиент Qdrant
    """
    # Проверяем, существует ли коллекция
    collections = client.get_collections().collections
    collection_exists = any(col.name == COLLECTION_NAME for col in collections)

    if collection_exists:
        client.delete_collection(collection_name=COLLECTION_NAME)


__all__ = [
    "down_revision",
    "downgrade",
    "revision",
    "upgrade",
]
