"""ORM модель пользовательского контента."""

# pyright: reportUninitializedInstanceVariable=false

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKeyConstraint, Index, SmallInteger, Text, text
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID  # noqa: N811
from sqlalchemy.orm import Mapped

from lib.domain.entities.ugc import UGC
from lib.domain.enums import UgcKind
from lib.domain.value_objects import PlaceId, RatingScore, UserId
from lib.infra.db.orm_models.base import SCHEMA, mapper_registry, metadata

ugc_kind_enum = ENUM("rating", "review", "comment", name="ugc_kind", schema=SCHEMA, create_type=False)

ugc_table = metadata.tables.get(f"{SCHEMA}.ugc")
if ugc_table is None:
    from sqlalchemy import Table

    ugc_table = Table(
        "ugc",
        metadata,
        Column("id", PostgresUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        Column("user_id", PostgresUUID(as_uuid=True), nullable=False),
        Column("place_id", PostgresUUID(as_uuid=True), nullable=False),
        Column("kind", ugc_kind_enum, nullable=False),  # type: ignore[arg-type]
        Column("rating", SmallInteger(), nullable=True),
        Column("text", Text(), nullable=True),
        Column("meta", JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb")),
        Column("is_deleted", Boolean(), nullable=False, server_default=text("false")),
        Column("created_at", DateTime(timezone=True), nullable=False, server_default=text("now()")),
        Column("updated_at", DateTime(timezone=True), nullable=False, server_default=text("now()")),
        ForeignKeyConstraint(["user_id"], [f"{SCHEMA}.user.id"], ondelete="CASCADE", name="fk_ugc_user"),
        ForeignKeyConstraint(["place_id"], [f"{SCHEMA}.place.id"], ondelete="CASCADE", name="fk_ugc_place"),
        CheckConstraint("rating IS NULL OR (rating >= 1 AND rating <= 5)", name="ck_ugc_rating_range"),
        Index("ix_ugc_place_id_created_at", "place_id", "created_at"),
        Index("ix_ugc_user_id_created_at", "user_id", "created_at"),
        Index("ix_ugc_kind", "kind"),
        Index("ix_ugc_is_deleted", "is_deleted"),
        schema=SCHEMA,
    )


class UGCORM:
    """ORM модель пользовательского контента."""

    __table__ = ugc_table

    id: Mapped[UUID]
    user_id: Mapped[UUID]
    place_id: Mapped[UUID]
    kind: Mapped[str]
    rating: Mapped[int | None]
    text: Mapped[str | None]
    meta: Mapped[dict[str, Any]]
    is_deleted: Mapped[bool]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]

    def to_domain(self) -> UGC:
        """Преобразует ORM модель в domain entity."""
        rating_score = None
        if self.rating is not None:
            rating_score = RatingScore(value=float(self.rating))

        return UGC(
            id=self.id,
            user_id=UserId(value=self.user_id),
            place_id=PlaceId(value=self.place_id),
            kind=UgcKind(self.kind),
            rating=rating_score,
            text=self.text,
            meta=self.meta,
            is_deleted=self.is_deleted,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, ugc: UGC) -> "UGCORM":
        """Создает ORM модель из domain entity."""
        instance = cls.__new__(cls)
        instance.id = ugc.id
        instance.user_id = ugc.user_id.value
        instance.place_id = ugc.place_id.value
        instance.kind = ugc.kind.value
        instance.rating = int(ugc.rating.value) if ugc.rating else None
        instance.text = ugc.text
        instance.meta = ugc.meta
        instance.is_deleted = ugc.is_deleted
        instance.created_at = ugc.created_at
        instance.updated_at = ugc.updated_at
        return instance


mapper_registry.map_imperatively(UGCORM, ugc_table)


__all__ = [
    "UGCORM",
    "ugc_kind_enum",
    "ugc_table",
]
