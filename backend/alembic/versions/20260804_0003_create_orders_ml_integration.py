"""create orders, product_channel_mapping, ml_credentials, webhook_events

Revision ID: 20260804_0003
Revises: 20260804_0002
Create Date: 2026-08-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260804_0003"
down_revision: str | None = "20260804_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("canal", sa.String(length=30), nullable=False),
        sa.Column("pedido_id_externo", sa.String(length=60), nullable=False),
        sa.Column("item_id_externo", sa.String(length=60), nullable=True),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("quantidade", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pendente_etiqueta"),
        sa.Column("etiqueta_gerada", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("etiqueta_url", sa.String(length=500), nullable=True),
        sa.Column("shipment_id_externo", sa.String(length=60), nullable=True),
        sa.Column("data_pedido", sa.DateTime(timezone=True), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "canal", "pedido_id_externo", name="uq_orders_tenant_canal_pedido"
        ),
        sa.CheckConstraint("canal IN ('mercado_livre')", name="ck_orders_canal_valid"),
        sa.CheckConstraint(
            "status IN ('pendente_etiqueta', 'etiqueta_gerada', 'despachado', 'cancelado')",
            name="ck_orders_status_valid",
        ),
    )
    op.create_index(op.f("ix_orders_id"), "orders", ["id"], unique=False)
    op.create_index(op.f("ix_orders_tenant_id"), "orders", ["tenant_id"], unique=False)

    op.create_table(
        "product_channel_mapping",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("canal", sa.String(length=30), nullable=False),
        sa.Column("item_id_externo", sa.String(length=60), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "canal", "item_id_externo", name="uq_mapping_tenant_canal_item"
        ),
        sa.CheckConstraint("canal IN ('mercado_livre')", name="ck_mapping_canal_valid"),
    )
    op.create_index(op.f("ix_product_channel_mapping_id"), "product_channel_mapping", ["id"], unique=False)
    op.create_index(
        op.f("ix_product_channel_mapping_tenant_id"), "product_channel_mapping", ["tenant_id"], unique=False
    )

    op.create_table(
        "ml_credentials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("ml_user_id", sa.String(length=60), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", name="uq_ml_credentials_tenant"),
    )
    op.create_index(op.f("ix_ml_credentials_id"), "ml_credentials", ["id"], unique=False)
    op.create_index(op.f("ix_ml_credentials_tenant_id"), "ml_credentials", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_ml_credentials_ml_user_id"), "ml_credentials", ["ml_user_id"], unique=False)

    op.create_table(
        "webhook_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("canal", sa.String(length=30), nullable=False, server_default="mercado_livre"),
        sa.Column("topic", sa.String(length=60), nullable=False),
        sa.Column("resource", sa.String(length=255), nullable=False),
        sa.Column("ml_notification_id", sa.String(length=120), nullable=True),
        sa.Column("payload_raw", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="recebido"),
        sa.Column("tentativas", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("erro_detalhe", sa.Text(), nullable=True),
        sa.Column("recebido_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("processado_em", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "ml_notification_id", name="uq_webhook_events_tenant_notification"
        ),
        sa.CheckConstraint("canal IN ('mercado_livre')", name="ck_webhook_events_canal_valid"),
        sa.CheckConstraint(
            "status IN ('recebido', 'processando', 'processado', 'erro', 'duplicado')",
            name="ck_webhook_events_status_valid",
        ),
    )
    op.create_index(op.f("ix_webhook_events_id"), "webhook_events", ["id"], unique=False)
    op.create_index(op.f("ix_webhook_events_tenant_id"), "webhook_events", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_webhook_events_tenant_id"), table_name="webhook_events")
    op.drop_index(op.f("ix_webhook_events_id"), table_name="webhook_events")
    op.drop_table("webhook_events")

    op.drop_index(op.f("ix_ml_credentials_ml_user_id"), table_name="ml_credentials")
    op.drop_index(op.f("ix_ml_credentials_tenant_id"), table_name="ml_credentials")
    op.drop_index(op.f("ix_ml_credentials_id"), table_name="ml_credentials")
    op.drop_table("ml_credentials")

    op.drop_index(op.f("ix_product_channel_mapping_tenant_id"), table_name="product_channel_mapping")
    op.drop_index(op.f("ix_product_channel_mapping_id"), table_name="product_channel_mapping")
    op.drop_table("product_channel_mapping")

    op.drop_index(op.f("ix_orders_tenant_id"), table_name="orders")
    op.drop_index(op.f("ix_orders_id"), table_name="orders")
    op.drop_table("orders")
