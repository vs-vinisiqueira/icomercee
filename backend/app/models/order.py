from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)

from app.database import Base


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "canal", "pedido_id_externo", name="uq_orders_tenant_canal_pedido"
        ),
        CheckConstraint("canal IN ('mercado_livre')", name="ck_orders_canal_valid"),
        CheckConstraint(
            "status IN ('pendente_etiqueta', 'etiqueta_gerada', 'despachado', 'cancelado')",
            name="ck_orders_status_valid",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    canal = Column(String(30), nullable=False)
    pedido_id_externo = Column(String(60), nullable=False)
    item_id_externo = Column(String(60), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    quantidade = Column(Integer, nullable=False, default=1)
    status = Column(String(30), nullable=False, default="pendente_etiqueta", server_default="pendente_etiqueta")
    etiqueta_gerada = Column(Boolean, nullable=False, default=False, server_default="false")
    etiqueta_url = Column(String(500), nullable=True)
    shipment_id_externo = Column(String(60), nullable=True)
    data_pedido = Column(DateTime(timezone=True), nullable=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    atualizado_em = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
