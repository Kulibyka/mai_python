"""ORM модель связи пользователя и роли."""

# pyright: reportUninitializedInstanceVariable=false

from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, DateTime, ForeignKeyConstraint, Index, PrimaryKeyConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID  # noqa: N811
from sqlalchemy.orm import Mapped

from lib.infra.db.orm_models.base import SCHEMA, mapper_registry, metadata

user_role_table = metadata.tables.get(f"{SCHEMA}.user_role")
if user_role_table is None:
    from sqlalchemy import Table

    user_role_table = Table(
        "user_role",
        metadata,
        Column("user_id", PostgresUUID(as_uuid=True), nullable=False),
        Column("role_id", PostgresUUID(as_uuid=True), nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False, server_default=text("now()")),
        PrimaryKeyConstraint("user_id", "role_id", name="pk_user_role"),
        ForeignKeyConstraint(["user_id"], [f"{SCHEMA}.user.id"], ondelete="CASCADE", name="fk_user_role_user"),
        ForeignKeyConstraint(["role_id"], [f"{SCHEMA}.role.id"], ondelete="CASCADE", name="fk_user_role_role"),
        Index("ix_user_role_role_id", "role_id"),
        schema=SCHEMA,
    )


class UserRoleORM:
    """ORM модель связи пользователя и роли."""

    __table__ = user_role_table

    user_id: Mapped[UUID]
    role_id: Mapped[UUID]
    created_at: Mapped[datetime]


mapper_registry.map_imperatively(UserRoleORM, user_role_table)


__all__ = [
    "UserRoleORM",
    "user_role_table",
]
