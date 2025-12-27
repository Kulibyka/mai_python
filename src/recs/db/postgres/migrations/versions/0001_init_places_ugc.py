"""
Initial tables

Revision ID: 0001_init_places_ugc
Revises:
Create Date: 2025-12-26 00:07:41.134948

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_init_places_ugc"
down_revision = None
branch_labels = None
depends_on = None

SCHEMA = "content"


def upgrade() -> None:
    """
    Upgrade schema.
    """
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};")

    op.create_table(
        "role",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("code", sa.String(64), nullable=False),  # e.g. "admin", "user"
        sa.Column("name", sa.String(128), nullable=False),  # human readable
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("code", name="uq_role_code"),
        schema=SCHEMA,
    )

    op.create_table(
        "user",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(320), nullable=True),
        sa.Column("username", sa.String(64), nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "profile", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")
        ),
        sa.Column(
            "preferences",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "meta", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")
        ),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("email", name="uq_user_email"),
        sa.UniqueConstraint("username", name="uq_user_username"),
        schema=SCHEMA,
    )
    op.create_index("ix_user_is_active", "user", ["is_active"], schema=SCHEMA)
    op.create_index("ix_user_created_at", "user", ["created_at"], schema=SCHEMA)

    op.create_table(
        "user_role",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("user_id", "role_id", name="pk_user_role"),
        sa.ForeignKeyConstraint(["user_id"], [f"{SCHEMA}.user.id"], name="fk_user_role_user", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], [f"{SCHEMA}.role.id"], name="fk_user_role_role", ondelete="CASCADE"),
        schema=SCHEMA,
    )
    op.create_index("ix_user_role_role_id", "user_role", ["role_id"], schema=SCHEMA)

    op.create_table(
        "place",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("osm_id", sa.String(64), nullable=False),  # "node:61669376"
        sa.Column("osm_type", sa.String(16), nullable=True),  # "node" / "way" / "relation" (если понадобится)
        sa.Column("name", sa.String(512), nullable=True),
        sa.Column("category_key", sa.String(64), nullable=True),  # "amenity"
        sa.Column("category_value", sa.String(128), nullable=True),  # "cinema"
        sa.Column("lat", sa.Numeric(9, 7), nullable=True),
        sa.Column("lon", sa.Numeric(10, 7), nullable=True),
        sa.Column(
            "tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")
        ),
        sa.Column(
            "address", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")
        ),
        sa.Column(
            "source", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("osm_id", name="uq_place_osm_id"),
        schema=SCHEMA,
    )
    op.create_index("ix_place_category", "place", ["category_key", "category_value"], schema=SCHEMA)
    op.create_index("ix_place_coords", "place", ["lat", "lon"], schema=SCHEMA)
    op.create_index("ix_place_is_active", "place", ["is_active"], schema=SCHEMA)

    # Создаём тип ENUM только если он не существует (в указанной схеме)
    op.execute(
        f"""
        DO $$ BEGIN
            CREATE TYPE {SCHEMA}.ugc_kind AS ENUM ('rating', 'review', 'comment');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """
    )

    # Создаём объект ENUM для использования в колонке (без попытки создания типа)
    ugc_kind = postgresql.ENUM("rating", "review", "comment", name="ugc_kind", schema=SCHEMA, create_type=False)

    op.create_table(
        "ugc",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("place_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kind", ugc_kind, nullable=False),  # type: ignore[arg-type]
        sa.Column("rating", sa.SmallInteger(), nullable=True),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column(
            "meta", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], [f"{SCHEMA}.user.id"], name="fk_ugc_user", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["place_id"], [f"{SCHEMA}.place.id"], name="fk_ugc_place", ondelete="CASCADE"),
        sa.CheckConstraint("rating IS NULL OR (rating >= 1 AND rating <= 5)", name="ck_ugc_rating_range"),
        schema=SCHEMA,
    )
    op.create_index("ix_ugc_place_id_created_at", "ugc", ["place_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_ugc_user_id_created_at", "ugc", ["user_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_ugc_kind", "ugc", ["kind"], schema=SCHEMA)
    op.create_index("ix_ugc_is_deleted", "ugc", ["is_deleted"], schema=SCHEMA)


def downgrade() -> None:
    """
    Downgrade schema.
    """
    op.drop_index("ix_ugc_is_deleted", table_name="ugc", schema=SCHEMA)
    op.drop_index("ix_ugc_kind", table_name="ugc", schema=SCHEMA)
    op.drop_index("ix_ugc_user_id_created_at", table_name="ugc", schema=SCHEMA)
    op.drop_index("ix_ugc_place_id_created_at", table_name="ugc", schema=SCHEMA)
    op.drop_table("ugc", schema=SCHEMA)

    op.drop_index("ix_place_is_active", table_name="place", schema=SCHEMA)
    op.drop_index("ix_place_coords", table_name="place", schema=SCHEMA)
    op.drop_index("ix_place_category", table_name="place", schema=SCHEMA)
    op.drop_table("place", schema=SCHEMA)

    op.drop_index("ix_user_role_role_id", table_name="user_role", schema=SCHEMA)
    op.drop_table("user_role", schema=SCHEMA)

    op.drop_index("ix_user_created_at", table_name="user", schema=SCHEMA)
    op.drop_index("ix_user_is_active", table_name="user", schema=SCHEMA)
    op.drop_table("user", schema=SCHEMA)

    op.drop_table("role", schema=SCHEMA)

    # Удаляем тип ENUM из схемы
    op.execute(f"DROP TYPE IF EXISTS {SCHEMA}.ugc_kind;")
