"""ORM модель места."""

# pyright: reportUninitializedInstanceVariable=false

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, Column, DateTime, Index, Numeric, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID  # noqa: N811
from sqlalchemy.orm import Mapped

from lib.domain.entities.place import Place
from lib.domain.value_objects import Coordinates, OsmId, PlaceId
from lib.infra.db.orm_models.base import SCHEMA, mapper_registry, metadata

place_table = metadata.tables.get(f"{SCHEMA}.place")
if place_table is None:
    from sqlalchemy import Table

    place_table = Table(
        "place",
        metadata,
        Column("id", PostgresUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        Column("osm_id", String(64), nullable=False),
        Column("osm_type", String(16), nullable=True),
        Column("name", String(512), nullable=True),
        Column("category_key", String(64), nullable=True),
        Column("category_value", String(128), nullable=True),
        Column("lat", Numeric(9, 7), nullable=True),
        Column("lon", Numeric(10, 7), nullable=True),
        Column("tags", JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb")),
        Column("address", JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb")),
        Column("source", JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb")),
        Column("is_active", Boolean(), nullable=False, server_default=text("true")),
        Column("created_at", DateTime(timezone=True), nullable=False, server_default=text("now()")),
        Column("updated_at", DateTime(timezone=True), nullable=False, server_default=text("now()")),
        UniqueConstraint("osm_id", name="uq_place_osm_id"),
        Index("ix_place_category", "category_key", "category_value"),
        Index("ix_place_coords", "lat", "lon"),
        Index("ix_place_is_active", "is_active"),
        schema=SCHEMA,
    )


class PlaceORM:
    """ORM модель места."""

    __table__ = place_table

    id: Mapped[UUID]
    osm_id: Mapped[str]
    osm_type: Mapped[str | None]
    name: Mapped[str | None]
    category_key: Mapped[str | None]
    category_value: Mapped[str | None]
    lat: Mapped[Decimal | None]
    lon: Mapped[Decimal | None]
    tags: Mapped[dict[str, Any]]
    address: Mapped[dict[str, Any]]
    source: Mapped[dict[str, Any]]
    is_active: Mapped[bool]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]

    def to_domain(self) -> Place:
        """Преобразует ORM модель в domain entity."""
        coordinates = None
        if self.lat is not None and self.lon is not None:
            coordinates = Coordinates(latitude=self.lat, longitude=self.lon)

        return Place(
            id=PlaceId(value=self.id),
            osm_id=OsmId(value=self.osm_id),
            osm_type=self.osm_type,
            name=self.name,
            category_key=self.category_key,
            category_value=self.category_value,
            coordinates=coordinates,
            tags=self.tags,
            address=self.address,
            source=self.source,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, place: Place) -> "PlaceORM":
        """Создает ORM модель из domain entity."""
        instance = cls.__new__(cls)
        instance.id = place.id.value
        instance.osm_id = place.osm_id.value
        instance.osm_type = place.osm_type
        instance.name = place.name
        instance.category_key = place.category_key
        instance.category_value = place.category_value
        instance.lat = place.coordinates.latitude if place.coordinates else None
        instance.lon = place.coordinates.longitude if place.coordinates else None
        instance.tags = place.tags
        instance.address = place.address
        instance.source = place.source
        instance.is_active = place.is_active
        instance.created_at = place.created_at
        instance.updated_at = place.updated_at
        return instance


mapper_registry.map_imperatively(PlaceORM, place_table)


__all__ = [
    "PlaceORM",
    "place_table",
]
