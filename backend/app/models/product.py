from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)

from app.database import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("tenant_id", "sku", name="uq_products_tenant_sku"),
        CheckConstraint("estoque_atual >= 0", name="ck_products_estoque_atual_nao_negativo"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    sku = Column(String(60), nullable=False)
    nome = Column(String(200), nullable=False)
    categoria = Column(String(100), nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    custo_compra = Column(Numeric(10, 2), nullable=False, default=0)
    preco_venda = Column(Numeric(10, 2), nullable=False, default=0)
    estoque_minimo = Column(Integer, nullable=False, default=0, server_default="0")
    estoque_atual = Column(Integer, nullable=False, default=0, server_default="0")
    ativo = Column(Boolean, nullable=False, default=True, server_default="true")
    criado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    atualizado_em = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
