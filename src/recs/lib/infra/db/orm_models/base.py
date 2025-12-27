"""
Базовые определения для ORM моделей.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import registry

SCHEMA = "content"
metadata = MetaData(schema=SCHEMA)
mapper_registry = registry()


__all__ = [
    "SCHEMA",
    "mapper_registry",
    "metadata",
]
