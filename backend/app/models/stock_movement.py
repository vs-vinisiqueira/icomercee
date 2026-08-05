from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)

from app.database import Base


class StockMovement(Base):
    __tablename__ = "stock_movements"
    __table_args__ = (
        CheckConstraint("tipo IN ('entrada', 'saida')", name="ck_stock_movements_tipo_valid"),
        CheckConstraint(
            "motivo IN ('compra_fornecedor', 'ajuste_manual', 'perda', 'baixa_pedido')",
            name="ck_stock_movements_motivo_valid",
        ),
        CheckConstraint("origem IN ('manual', 'pedido')", name="ck_stock_movements_origem_valid"),
        CheckConstraint("quantidade > 0", name="ck_stock_movements_quantidade_positiva"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    tipo = Column(String(10), nullable=False)
    quantidade = Column(Integer, nullable=False)
    motivo = Column(String(30), nullable=False)
    origem = Column(String(10), nullable=False)
    referencia_pedido_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    custo_unitario = Column(Numeric(10, 2), nullable=True)
    observacao = Column(Text, nullable=True)
    criado_por = Column(Integer, ForeignKey("users.id"), nullable=False)
    criado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
