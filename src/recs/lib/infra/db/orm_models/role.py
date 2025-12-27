"""ORM модель роли."""

# pyright: reportUninitializedInstanceVariable=false

from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, DateTime, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID  # noqa: N811
from sqlalchemy.orm import Mapped

from lib.domain.entities.role import Role
from lib.domain.enums import RoleName
from lib.domain.value_objects import RoleId
from lib.infra.db.orm_models.base import SCHEMA, mapper_registry, metadata

role_table = metadata.tables.get(f"{SCHEMA}.role")
if role_table is None:
    from sqlalchemy import Table

    role_table = Table(
        "role",
        metadata,
        Column("id", PostgresUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        Column("code", String(64), nullable=False),
        Column("name", String(128), nullable=False),
        Column("description", Text(), nullable=True),
        Column("created_at", DateTime(timezone=True), nullable=False, server_default=text("now()")),
        Column("updated_at", DateTime(timezone=True), nullable=False, server_default=text("now()")),
        UniqueConstraint("code", name="uq_role_code"),
        schema=SCHEMA,
    )


class RoleORM:
    """ORM модель роли."""

    __table__ = role_table

    id: Mapped[UUID]
    code: Mapped[str]
    name: Mapped[str]
    description: Mapped[str | None]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]

    def to_domain(self) -> Role:
        """Преобразует ORM модель в domain entity."""
        return Role(
            id=RoleId(value=self.id),
            code=RoleName(self.code),
            name=self.name,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, role: Role) -> "RoleORM":
        """Создает ORM модель из domain entity."""
        instance = cls.__new__(cls)
        instance.id = role.id.value
        instance.code = role.code.value
        instance.name = role.name
        instance.description = role.description
        instance.created_at = role.created_at
        instance.updated_at = role.updated_at
        return instance


mapper_registry.map_imperatively(RoleORM, role_table)


__all__ = [
    "RoleORM",
    "role_table",
]
