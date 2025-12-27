"""ORM модель пользователя."""

# pyright: reportUninitializedInstanceVariable=false

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, Column, DateTime, Index, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID  # noqa: N811
from sqlalchemy.orm import Mapped

from lib.domain.entities.user import User
from lib.domain.value_objects import Email, UserId, Username
from lib.infra.db.orm_models.base import SCHEMA, mapper_registry, metadata

user_table = metadata.tables.get(f"{SCHEMA}.user")
if user_table is None:
    from sqlalchemy import Table

    user_table = Table(
        "user",
        metadata,
        Column("id", PostgresUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        Column("email", String(320), nullable=True),
        Column("username", String(64), nullable=True),
        Column("password_hash", String(255), nullable=True),
        Column("is_active", Boolean(), nullable=False, server_default=text("true")),
        Column("is_verified", Boolean(), nullable=False, server_default=text("false")),
        Column("profile", JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb")),
        Column("preferences", JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb")),
        Column("meta", JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb")),
        Column("last_login_at", DateTime(timezone=True), nullable=True),
        Column("created_at", DateTime(timezone=True), nullable=False, server_default=text("now()")),
        Column("updated_at", DateTime(timezone=True), nullable=False, server_default=text("now()")),
        UniqueConstraint("email", name="uq_user_email"),
        UniqueConstraint("username", name="uq_user_username"),
        Index("ix_user_is_active", "is_active"),
        Index("ix_user_created_at", "created_at"),
        schema=SCHEMA,
    )


class UserORM:
    """ORM модель пользователя."""

    __table__ = user_table

    id: Mapped[UUID]
    email: Mapped[str | None]
    username: Mapped[str | None]
    password_hash: Mapped[str | None]
    is_active: Mapped[bool]
    is_verified: Mapped[bool]
    profile: Mapped[dict[str, Any]]
    preferences: Mapped[dict[str, Any]]
    meta: Mapped[dict[str, Any]]
    last_login_at: Mapped[datetime | None]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]

    def to_domain(self) -> User:
        """Преобразует ORM модель в domain entity."""
        return User(
            id=UserId(value=self.id),
            email=Email(value=self.email) if self.email else None,
            username=Username(value=self.username) if self.username else None,
            password_hash=self.password_hash,
            is_active=self.is_active,
            is_verified=self.is_verified,
            profile=self.profile,
            preferences=self.preferences,
            meta=self.meta,
            last_login_at=self.last_login_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, user: User) -> "UserORM":
        """Создает ORM модель из domain entity."""
        instance = cls.__new__(cls)
        instance.id = user.id.value
        instance.email = user.email.value if user.email else None
        instance.username = user.username.value if user.username else None
        instance.password_hash = user.password_hash
        instance.is_active = user.is_active
        instance.is_verified = user.is_verified
        instance.profile = user.profile
        instance.preferences = user.preferences
        instance.meta = user.meta
        instance.last_login_at = user.last_login_at
        instance.created_at = user.created_at
        instance.updated_at = user.updated_at
        return instance


mapper_registry.map_imperatively(UserORM, user_table)


__all__ = [
    "UserORM",
    "user_table",
]
