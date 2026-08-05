"""create stock_movements table

Revision ID: 20260804_0004
Revises: 20260804_0003
Create Date: 2026-08-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260804_0004"
down_revision: str | None = "20260804_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "stock_movements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=10), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("motivo", sa.String(length=30), nullable=False),
        sa.Column("origem", sa.String(length=10), nullable=False),
        sa.Column("referencia_pedido_id", sa.Integer(), nullable=True),
        sa.Column("custo_unitario", sa.Numeric(10, 2), nullable=True),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.Column("criado_por", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["referencia_pedido_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["criado_por"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("tipo IN ('entrada', 'saida')", name="ck_stock_movements_tipo_valid"),
        sa.CheckConstraint(
            "motivo IN ('compra_fornecedor', 'ajuste_manual', 'perda', 'baixa_pedido')",
            name="ck_stock_movements_motivo_valid",
        ),
        sa.CheckConstraint("origem IN ('manual', 'pedido')", name="ck_stock_movements_origem_valid"),
        sa.CheckConstraint("quantidade > 0", name="ck_stock_movements_quantidade_positiva"),
    )
    op.create_index(op.f("ix_stock_movements_id"), "stock_movements", ["id"], unique=False)
    op.create_index(op.f("ix_stock_movements_tenant_id"), "stock_movements", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_stock_movements_product_id"), "stock_movements", ["product_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_stock_movements_product_id"), table_name="stock_movements")
    op.drop_index(op.f("ix_stock_movements_tenant_id"), table_name="stock_movements")
    op.drop_index(op.f("ix_stock_movements_id"), table_name="stock_movements")
    op.drop_table("stock_movements")
